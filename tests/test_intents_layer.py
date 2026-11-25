"""Integrity checks for the modular intents layer on asset dossiers.

Two levels:
  1. The GENERIC intent -- an open object that can record any want.
  2. The INSURANCE WISH -- a generic intent plus stricter insurance fields.

The layer's iron rule: intents are WANTS, never outcomes. Whether anyone
passes any gate is the gatekeeper's business (oracles, registries,
contracts) -- TestTown only records what the world wanted first.
"""

from datetime import date
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
CITIZENS = ROOT / "dossiers" / "citizens"

# The rules live in tools/validate_intents.py so consumers can reuse them.
# The tests here prove the rules behave, and that the town obeys them.
sys.path.insert(0, str(ROOT / "tools"))
from validate_intents import (  # noqa: E402  (import after the path tweak)
    all_intent_problems,
    flatten_keys,
    generic_intent_problems,
    insurance_wish_problems,
    load_asset_dossiers,
    load_examples,
)

# Key names that would mean somebody stored a secret in a dossier.
SECRET_KEYS = {"seed", "seedPhrase", "mnemonic", "privateKey", "secretKey"}


class GenericIntentTests(unittest.TestCase):
    """The intent object can be anything: these use made-up, non-insurance wants."""

    NOW = date(2026, 11, 24)

    def test_minimal_intent_is_valid(self):
        intent = {"wants": "Sell the piano", "expressedAt": "2026-11-01", "status": "open"}
        self.assertEqual(generic_intent_problems(intent, self.NOW), [])

    def test_unknown_category_with_free_form_block_is_valid(self):
        intent = {
            "wants": "Lend the van to a neighbor", "expressedAt": "2026-11-01",
            "status": "withdrawn", "category": "lending",
            "lending": {"toCitizenSlug": "colin-mcbride", "anything": ["goes", "here"]},
        }
        self.assertEqual(generic_intent_problems(intent, self.NOW), [])

    def test_broken_generic_intents_are_caught(self):
        base = {"wants": "Sell the piano", "expressedAt": "2026-11-01", "status": "open"}
        broken = [
            {**base, "wants": ""},
            {**base, "status": "approved"},
            {**base, "expiresAt": "2026-11-10"},                      # open but stale
            {**base, "status": "expired"},                            # no expiresAt
            {**base, "status": "expired", "expiresAt": "2027-01-01"},  # not yet
            {**base, "startDate": "2026-10-01"},                      # before expressed
            {**base, "category": "lending"},                          # no details block
            {**base, "approved": True},                               # an outcome
        ]
        for intent in broken:
            self.assertNotEqual(generic_intent_problems(intent, self.NOW), [], intent)


class WorkedExampleTests(unittest.TestCase):
    """examples/intents-examples.json is documentation that cannot go stale:
    every example must behave exactly as its 'expectValid' says."""

    def test_every_example_behaves_as_documented(self):
        examples = load_examples()
        self.assertGreaterEqual(len(examples), 10)
        for example in examples:
            problems = all_intent_problems(
                example["intent"], date.fromisoformat(example["frozenNow"])
            )
            self.assertEqual(not problems, example["expectValid"], f"{example['id']}: {problems}")

    def test_examples_explain_themselves(self):
        ids = [example["id"] for example in load_examples()]
        self.assertEqual(len(ids), len(set(ids)))
        for example in load_examples():
            self.assertTrue(example["title"] and example["teaches"], example["id"])
            # Broken-on-purpose examples say so in their id, so nobody copies one.
            self.assertEqual(example["id"].startswith("BROKEN-"), not example["expectValid"])


class TestTownIntentFixtureTests(unittest.TestCase):
    """The real town: the seven wallets and the wants their owners voiced."""

    def setUp(self):
        self.with_intents = {
            slug: d for slug, d in load_asset_dossiers() if d.get("intents")
        }

    def test_every_fixture_intent_passes_the_generic_rules(self):
        for slug, dossier in self.with_intents.items():
            frozen_now = date.fromisoformat(dossier["holdings"]["asOf"])
            for intent in dossier["intents"]:
                self.assertEqual(generic_intent_problems(intent, frozen_now), [], slug)

    def test_every_insurance_wish_passes_the_insurance_rules(self):
        wishes = 0
        for slug, dossier in self.with_intents.items():
            for intent in dossier["intents"]:
                if intent.get("category") == "insurance":
                    wishes += 1
                    self.assertEqual(insurance_wish_problems(intent), [], slug)
        self.assertEqual(wishes, 8)

    def test_broken_insurance_wishes_are_caught(self):
        good = {
            "wants": "Insure this wallet for $500", "expressedAt": "2026-11-01",
            "startDate": "2026-12-01", "expiresAt": "2027-01-30", "status": "open",
            "category": "insurance", "insurance": {"wish": "cover-asset", "coverageUsd": 500},
        }
        self.assertEqual(insurance_wish_problems(good), [])
        without_start = {k: v for k, v in good.items() if k != "startDate"}
        without_expiry = {k: v for k, v in good.items() if k != "expiresAt"}
        zero_cover = {**good, "insurance": {"wish": "cover-asset", "coverageUsd": 0}}
        odd_wish = {**good, "insurance": {"wish": "win-lottery", "coverageUsd": 500}}
        for intent in (without_start, without_expiry, zero_cover, odd_wish):
            self.assertNotEqual(insurance_wish_problems(intent), [], intent)

    def test_at_most_one_open_insurance_wish_per_asset(self):
        for slug, dossier in self.with_intents.items():
            open_wishes = [
                i for i in dossier["intents"]
                if i.get("category") == "insurance" and i["status"] == "open"
            ]
            self.assertLessEqual(len(open_wishes), 1, slug)

    def test_population_includes_open_and_expired_intents(self):
        statuses = [i["status"] for d in self.with_intents.values() for i in d["intents"]]
        self.assertIn("expired", statuses)
        self.assertIn("open", statuses)

    def test_seven_wallet_assets_carry_intents(self):
        wallets = {
            slug for slug, d in self.with_intents.items()
            if d.get("assetKind") == "crypto-wallet"
        }
        self.assertEqual(len(wallets), 7, sorted(wallets))

    def test_wallet_identity_anchor_is_the_address(self):
        for slug, dossier in self.with_intents.items():
            if dossier.get("assetKind") != "crypto-wallet":
                continue
            anchor = dossier["identityAnchor"]
            self.assertEqual(anchor["kind"], "wallet-address", slug)
            self.assertTrue(anchor["value"], slug)

    def test_holdings_are_marked_mock_and_fictional(self):
        for slug, dossier in self.with_intents.items():
            if dossier.get("assetKind") != "crypto-wallet":
                continue
            holdings = dossier["holdings"]
            self.assertEqual(holdings["evidence"], "MOCK", slug)
            self.assertIs(holdings["fictional"], True, slug)
            self.assertGreater(holdings["balanceUsd"], 0, slug)
            self.assertIn(holdings["chain"], {"bitcoin", "ethereum", "midnight"}, slug)

    def test_owner_backlink_is_bidirectional(self):
        for slug, dossier in self.with_intents.items():
            owner_slug = dossier.get("ownerCitizenSlug")
            self.assertTrue(owner_slug, slug)
            citizen_path = CITIZENS / owner_slug / "dossier.json"
            self.assertTrue(citizen_path.exists(), f"{slug}: missing {owner_slug}")
            citizen = json.loads(citizen_path.read_text())
            self.assertIn(
                slug,
                citizen.get("householdSlugs", {}).get("assets", []),
                f"{owner_slug} does not list {slug}",
            )

    def test_no_secrets_anywhere(self):
        for slug, dossier in load_asset_dossiers():
            for key in flatten_keys(dossier):
                self.assertNotIn(key.split(".")[-1], SECRET_KEYS, f"{slug}: {key}")

    def test_honesty_spine_present(self):
        for slug, dossier in self.with_intents.items():
            self.assertEqual(dossier["schema"], "testtown/dossier/v0.1", slug)
            self.assertEqual(dossier["honesty"]["role"], "AUTHENTIC", slug)


if __name__ == "__main__":
    unittest.main()
