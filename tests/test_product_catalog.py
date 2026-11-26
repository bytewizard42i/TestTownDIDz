"""Integrity checks for the product catalog: what TestTown's shops sell.

Four promises are tested here:
  1. Every product obeys the shape rules, and broken shapes are caught.
  2. A product is NEVER a customer record or an outcome. It may say what it
     requires; it may never say who bought it or who passed.
  3. Products and organizations point at each other. An AUTHENTIC product is
     listed by its underwriter and by every seller. The VILLAIN product is
     listed by nobody, and that missing backlink is how it is caught.
  4. The matcher ("the wish meets the shelf") gives the documented answers
     for the town's real wishes, for a horse as well as for wallets.
"""

from pathlib import Path
import copy
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / "dossiers"

# The rules live in tools/ so consumers (and a private overlay) can reuse them.
sys.path.insert(0, str(ROOT / "tools"))
from validate_catalog import (  # noqa: E402  (import after the path tweak)
    all_product_problems,
    load_examples,
    load_products,
    named_product_notes,
    product_problems,
    products_that_fit,
    reasons_product_does_not_fit,
)
from validate_intents import flatten_keys, load_asset_dossiers  # noqa: E402

SECRET_KEYS = {"seed", "seedPhrase", "mnemonic", "privateKey", "secretKey"}
INSURER = "ironclad-insurance-group"
EXCHANGE = "quarry-street-exchange"


def load_dossier(category, slug):
    return json.loads((DOSSIERS / category / slug / "dossier.json").read_text())


def insurance_wish(amount, product_slug=None):
    """A minimal open insurance wish for the matcher tests."""
    details = {"wish": "cover-asset", "coverageUsd": amount}
    if product_slug:
        details["productSlug"] = product_slug
    return {"wants": "Insure this", "expressedAt": "2026-11-01", "startDate": "2026-12-01",
            "expiresAt": "2027-01-30", "status": "open", "category": "insurance",
            "insurance": details}


class ProductShapeTests(unittest.TestCase):
    def setUp(self):
        self.products = load_products()
        self.good = self.products["wallet-theft-cover-starter"]

    def test_every_town_product_is_well_formed(self):
        self.assertGreaterEqual(len(self.products), 6)
        for slug, product in self.products.items():
            self.assertEqual(all_product_problems(product), [], slug)
            self.assertEqual(product["slug"], slug)
            self.assertEqual(product["schema"], "testtown/dossier/v0.1", slug)

    def test_broken_products_are_caught(self):
        def changed(path, value):
            """A copy of the good product with one nested field replaced."""
            product = copy.deepcopy(self.good)
            node = product
            for key in path[:-1]:
                node = node[key]
            node[path[-1]] = value
            return product

        broken = [
            changed(["category"], "asset"),
            changed(["displayName"], ""),
            changed(["underwriterOrganizationSlug"], ""),
            changed(["sellerOrganizationSlugs"], []),
            changed(["availability", "status"], "discontinued"),
            changed(["availability", "listedAt"], "2027-06-01"),        # on sale before listed
            changed(["availability", "withdrawnAt"], "2026-10-10"),     # dated but not withdrawn
            changed(["insurance", "covers", "dossierCategory"], "citizen"),
            changed(["insurance", "covers", "kinds"], []),
            changed(["insurance", "peril"], ""),
            changed(["insurance", "coverageUsd"], {"min": 2000, "max": 100}),
            changed(["insurance", "coverageUsd"], {"min": 0, "max": 100}),
            changed(["insurance", "deductibleUsd"], -1),
            changed(["insurance", "deductibleUsd"], 1000),              # swallows the cover
            changed(["insurance", "premiumUsdPerYear"], 0),
            changed(["insurance", "termMonths"], 1.5),
            changed(["insurance", "requires"], "identity-check"),       # a string, not a list
        ]
        for product in broken:
            self.assertNotEqual(all_product_problems(product), [], product)

    def test_unknown_product_kind_with_free_form_block_is_valid(self):
        product = {
            "category": "product", "slug": "van-hire", "displayName": "Van Hire",
            "productKind": "rental", "rental": {"anything": ["goes", "here"]},
            "underwriterOrganizationSlug": "quarry-road-trucking",
            "sellerOrganizationSlugs": ["quarry-road-trucking"],
            "availability": {"status": "on-sale", "listedAt": "2026-01-01", "asOf": "2026-11-25"},
        }
        self.assertEqual(all_product_problems(product), [])
        without_block = {k: v for k, v in product.items() if k != "rental"}
        self.assertNotEqual(product_problems(without_block), [])

    def test_availability_covers_all_three_stages(self):
        statuses = {p["availability"]["status"] for p in self.products.values()}
        self.assertEqual(statuses, {"announced", "on-sale", "withdrawn"})

    def test_the_catalog_is_not_only_about_wallets(self):
        categories = {p["insurance"]["covers"]["dossierCategory"] for p in self.products.values()}
        self.assertEqual(categories, {"asset", "animal"})


class NeverACustomerRecordTests(unittest.TestCase):
    """The rule that must never bend: a product is a menu, not a sales ledger."""

    def setUp(self):
        self.good = load_products()["wallet-theft-cover-starter"]

    def test_a_product_naming_a_customer_is_rejected(self):
        for key in ("customers", "policyholders", "issuedTo", "insuredCitizenSlug"):
            product = copy.deepcopy(self.good)
            product["insurance"][key] = ["bonnie-lachance"]
            self.assertTrue(any("names a customer" in p for p in product_problems(product)), key)

    def test_a_product_recording_an_outcome_is_rejected(self):
        for key in ("approved", "declined", "kycPassed", "bound"):
            product = copy.deepcopy(self.good)
            product["insurance"][key] = True
            self.assertTrue(any("encodes an outcome" in p for p in product_problems(product)), key)

    def test_no_town_product_mentions_any_citizen(self):
        citizen_slugs = {folder.name for folder in (DOSSIERS / "citizens").iterdir()}
        for slug, product in load_products().items():
            text = json.dumps(product)
            for citizen in citizen_slugs:
                self.assertNotIn(citizen, text, f"{slug} mentions {citizen}")

    def test_no_secrets_in_products(self):
        for slug, product in load_products().items():
            for key in flatten_keys(product):
                self.assertNotIn(key.split(".")[-1], SECRET_KEYS, f"{slug}: {key}")


class StorefrontTests(unittest.TestCase):
    """Products and organizations must agree about who sells what."""

    def setUp(self):
        self.products = load_products()
        self.authentic = {s: p for s, p in self.products.items() if p["honesty"]["role"] == "AUTHENTIC"}
        self.villains = {s: p for s, p in self.products.items() if p["honesty"]["role"] == "VILLAIN"}
        self.orgs = {
            folder.name: json.loads((folder / "dossier.json").read_text())
            for folder in (DOSSIERS / "organizations").iterdir()
        }

    def test_authentic_products_are_listed_by_underwriter_and_every_seller(self):
        for slug, product in self.authentic.items():
            underwriter = self.orgs[product["underwriterOrganizationSlug"]]
            self.assertEqual(underwriter["honesty"]["role"], "AUTHENTIC", slug)
            self.assertIn(slug, underwriter["storefront"]["underwrites"], slug)
            for seller in product["sellerOrganizationSlugs"]:
                self.assertIn(slug, self.orgs[seller]["storefront"]["sells"], f"{seller} / {slug}")

    def test_storefronts_list_only_products_that_exist_and_point_back(self):
        for org_slug, org in self.orgs.items():
            storefront = org.get("storefront")
            if not storefront:
                continue
            for slug in storefront["underwrites"]:
                self.assertEqual(self.authentic[slug]["underwriterOrganizationSlug"], org_slug)
            for slug in storefront["sells"]:
                self.assertIn(org_slug, self.authentic[slug]["sellerOrganizationSlugs"])

    def test_the_insurer_and_the_exchange_both_have_a_shelf(self):
        self.assertGreaterEqual(len(self.orgs[INSURER]["storefront"]["underwrites"]), 5)
        exchange_shelf = self.orgs[EXCHANGE]["storefront"]
        self.assertGreaterEqual(len(exchange_shelf["sells"]), 3)
        # The exchange sells cover; it does not carry the risk itself.
        self.assertEqual(exchange_shelf["underwrites"], [])

    def test_villain_product_is_well_formed_but_nobody_honest_lists_it(self):
        self.assertEqual(len(self.villains), 1)
        for slug, product in self.villains.items():
            # Identical schema: a shape check alone can NOT catch it.
            self.assertEqual(all_product_problems(product), [], slug)
            self.assertTrue(product["honesty"]["fraudMechanism"], slug)
            # The tell: the underwriter it names never listed it.
            claimed_underwriter = self.orgs[product["underwriterOrganizationSlug"]]
            self.assertEqual(claimed_underwriter["honesty"]["role"], "AUTHENTIC")
            self.assertNotIn(slug, claimed_underwriter["storefront"]["underwrites"])
            for org in self.orgs.values():
                shelf = org.get("storefront", {})
                self.assertNotIn(slug, shelf.get("sells", []) + shelf.get("underwrites", []))

    def test_product_sheets_match_their_committed_hash(self):
        for slug, product in self.products.items():
            for document in product["documents"]:
                sheet = DOSSIERS / "products" / slug / document["file"]
                self.assertEqual(hashlib.sha256(sheet.read_bytes()).hexdigest(), document["sha256"], slug)


class WishMeetsShelfTests(unittest.TestCase):
    """The matcher is a lookup, not a decision. These pin down its answers."""

    def setUp(self):
        self.products = load_products()
        self.wallet = load_dossier("assets", "lachance-tips-wallet")
        self.horse = load_dossier("animals", "ember-the-broodmare")

    def test_each_amount_fits_exactly_one_wallet_product(self):
        expected = {100: "starter", 1000: "starter", 1001: "standard", 5000: "standard",
                    5001: "plus", 25000: "plus"}
        for amount, size in expected.items():
            self.assertEqual(products_that_fit(insurance_wish(amount), self.wallet, self.products),
                             [f"wallet-theft-cover-{size}"], amount)

    def test_amounts_nobody_sells_get_an_empty_answer(self):
        for amount in (50, 25001, 1_000_000):
            self.assertEqual(products_that_fit(insurance_wish(amount), self.wallet, self.products), [])

    def test_same_matcher_serves_a_horse(self):
        self.assertEqual(products_that_fit(insurance_wish(12000), self.horse, self.products),
                         ["equine-mortality-cover"])

    def test_withdrawn_announced_and_villain_products_never_match(self):
        for amount in (100, 500, 5000, 50000):
            for subject in (self.wallet, self.horse, load_dossier("assets", "mcbride-work-van")):
                for slug in products_that_fit(insurance_wish(amount), subject, self.products):
                    product = self.products[slug]
                    self.assertEqual(product["availability"]["status"], "on-sale", slug)
                    self.assertEqual(product["honesty"]["role"], "AUTHENTIC", slug)
        # The van's product exists but is only announced: nothing fits yet.
        van = load_dossier("assets", "mcbride-work-van")
        self.assertEqual(products_that_fit(insurance_wish(20000), van, self.products), [])
        self.assertIn("not on sale", reasons_product_does_not_fit(
            insurance_wish(20000), van, self.products["vehicle-theft-cover"]))

    def test_a_wish_naming_a_missing_product_is_a_fixture_problem(self):
        problems, mismatches = named_product_notes(
            insurance_wish(500, "no-such-product"), self.wallet, self.products)
        self.assertTrue(problems)
        self.assertEqual(mismatches, [])

    def test_a_product_blind_wish_has_nothing_to_check(self):
        self.assertEqual(named_product_notes(insurance_wish(500), self.wallet, self.products), ([], []))


class TownWishesAgainstTheShelfTests(unittest.TestCase):
    """The real town: seven wallets, their open wishes, and the shelf."""

    def setUp(self):
        self.products = load_products()
        self.open_wishes = [
            (slug, asset, intent)
            for slug, asset in load_asset_dossiers()
            for intent in asset.get("intents", [])
            if intent.get("category") == "insurance" and intent["status"] == "open"
        ]

    def test_every_open_wish_finds_exactly_one_product(self):
        self.assertEqual(len(self.open_wishes), 7)
        for slug, asset, intent in self.open_wishes:
            self.assertEqual(len(products_that_fit(intent, asset, self.products)), 1, slug)

    def test_no_town_wish_names_a_product_that_does_not_exist(self):
        for slug, asset, intent in self.open_wishes:
            problems, _ = named_product_notes(intent, asset, self.products)
            self.assertEqual(problems, [], slug)

    def test_some_wishes_name_a_product_and_some_stay_blind(self):
        named = {slug: intent["insurance"]["productSlug"]
                 for slug, _, intent in self.open_wishes if "productSlug" in intent["insurance"]}
        self.assertEqual(named, {"zhao-savings-wallet": "wallet-theft-cover-plus",
                                 "quist-bitcoin-wallet": "wallet-theft-cover-plus"})

    def test_mei_lin_named_the_right_product_and_harold_the_wrong_one(self):
        notes = {slug: named_product_notes(intent, asset, self.products)
                 for slug, asset, intent in self.open_wishes}
        # Mei-Lin ran her own numbers: $10,000 fits Plus.
        self.assertEqual(notes["zhao-savings-wallet"], ([], []))
        # Harold wants "the good one" for $1,000: below Plus's minimum. The
        # fixture is fine; the ASK is the mismatch a consumer has to handle.
        self.assertEqual(notes["quist-bitcoin-wallet"],
                         ([], ["asks for less than the product's minimum"]))


class WorkedExampleTests(unittest.TestCase):
    """examples/catalog-examples.json is documentation that cannot go stale."""

    def test_every_example_behaves_as_documented(self):
        examples = load_examples()
        self.assertGreaterEqual(len(examples), 10)
        for example in examples:
            problems = all_product_problems(example["product"])
            self.assertEqual(not problems, example["expectValid"], f"{example['id']}: {problems}")

    def test_examples_explain_themselves(self):
        ids = [example["id"] for example in load_examples()]
        self.assertEqual(len(ids), len(set(ids)))
        for example in load_examples():
            self.assertTrue(example["title"] and example["teaches"], example["id"])
            # Broken-on-purpose examples say so in their id, so nobody copies one.
            self.assertEqual(example["id"].startswith("BROKEN-"), not example["expectValid"])


if __name__ == "__main__":
    unittest.main()
