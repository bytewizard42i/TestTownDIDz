"""Validate the product catalog: what TestTown's shops have on the shelf.

WHAT THIS IS
    A "product" is something an organization SELLS to anyone who walks in:
    "wallet theft cover, up to $1,000, $18 a year". It is the mirror image of
    an intent. An intent is a citizen saying "I want my wallet insured"; a
    product is a shop saying "we sell wallet insurance, on these terms".

    This module holds the rules that decide whether a product is well formed,
    plus a small MATCHER that answers "which products on the shelf could
    serve this wish?". The tests import it, and you can run it by hand:

        python3 tools/validate_catalog.py

    Exit code 0 means everything is fine; 1 means something is off.

A PRODUCT IS NOT AN OFFER, AND NOT A POLICY
    Three things get called "policy" in everyday speech. Only the first one
    lives in TestTown:

      1. PRODUCT   a standing entry in a shop's catalog, the same for
                   everybody. A fact about the world, like a diner's menu.
                   LIVES HERE.
      2. OFFER     a shop's answer to ONE person's ask ("yes, Bonnie, $18").
                   That is the result of somebody's checks.  NOT HERE.
      3. POLICY    one person bound to one set of terms.     NOT HERE.

    Offers and policies are OUTCOMES. They belong to whoever made the
    decision (the insurer's own system), exactly as with intents. So a
    product never names a customer, and never says who qualifies.

THE RULE THAT MUST NEVER BEND (same rule as the intents layer)
    A product may say what it REQUIRES ("an identity check"). It may never
    say who PASSED. `requires` is a list of generic check names; the keys in
    FORBIDDEN_OUTCOME_KEYS and FORBIDDEN_CUSTOMER_KEYS are rejected anywhere
    inside a product.

HOW A PRIVATE OVERLAY USES THIS FILE
    A private repo can keep its own products (real terms that must not be
    public) in the same shape and check them with these same functions:
    call load_products(folder=<its own folder>) and product_problems(...).
    The shape is public; the numbers need not be.
"""

from datetime import date
from pathlib import Path
import json
import sys

# The intents rules are the older sibling of this file. We reuse its key
# walker and its outcome list so the two layers can never disagree about
# what counts as "smuggling in a gate's decision".
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_intents import FORBIDDEN_OUTCOME_KEYS, flatten_keys  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_FOLDER = ROOT / "dossiers" / "products"
EXAMPLES_FILE = ROOT / "examples" / "catalog-examples.json"

# The three stages a product can be frozen at.
#   announced  promised, not yet for sale (listedAt is still in the future)
#   on-sale    on the shelf today
#   withdrawn  taken off the shelf; kept as history, like an expired intent
# IDEA: "sold-out" (a capacity limit was reached) and "suspended" (a
# regulator paused it) are natural additions once a fixture needs them.
VALID_AVAILABILITY_STATUSES = {"announced", "on-sale", "withdrawn"}

# Keys that would turn a catalog entry into a customer record. A product is
# the same for everybody, so it has no business naming anybody.
FORBIDDEN_CUSTOMER_KEYS = {
    "customers", "customer", "policyholders", "policyholder", "insured",
    "insuredCitizenSlug", "issuedTo", "ownerCitizenSlug", "soldTo",
}

# Which kinds of dossier a product can be about. An insurance product covers
# a THING (an asset) or a LIVING THING (an animal).
# IDEA: "citizen" (health or life cover on a person) is the obvious next
# entry. It is left out until a fixture needs it, because cover on a person
# raises privacy questions that cover on a watch does not.
COVERABLE_DOSSIER_CATEGORIES = {"asset", "animal"}


def _is_positive_number(value):
    """True for 5 or 5.0, False for 0, -1, "5", None and True/False."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def product_problems(product):
    """Check the rules EVERY product obeys. Returns a list of problem strings.

    An empty list means the product is fine. Like the intents checker, we
    return every problem at once instead of stopping at the first.

    "Now" for a product is its own availability.asOf date, never the real
    clock, so a fixture means the same thing whenever the tests run.
    """
    problems = []

    # --- the spine every dossier shares -----------------------------------
    if product.get("category") != "product":
        problems.append("category must be 'product'")
    for field in ("slug", "displayName", "productKind"):
        if not product.get(field):
            problems.append(f"missing '{field}'")

    # --- who stands behind it, and who sells it -----------------------------
    # The underwriter carries the risk; the sellers put it on a shelf. They
    # can be the same organization. Both are slugs of organization dossiers.
    if not product.get("underwriterOrganizationSlug"):
        problems.append("missing 'underwriterOrganizationSlug'")
    sellers = product.get("sellerOrganizationSlugs")
    if not isinstance(sellers, list) or not sellers:
        problems.append("needs at least one seller in 'sellerOrganizationSlugs'")

    # --- availability: listedAt -> (withdrawnAt) ------------------------------
    availability = product.get("availability") or {}
    status = availability.get("status")
    if status not in VALID_AVAILABILITY_STATUSES:
        problems.append("bad availability status")
    if "listedAt" not in availability or "asOf" not in availability:
        # Without these two dates none of the date checks below can run.
        return problems + ["availability needs 'listedAt' and 'asOf'"]
    listed = date.fromisoformat(availability["listedAt"])
    frozen_now = date.fromisoformat(availability["asOf"])
    withdrawn_at = availability.get("withdrawnAt")

    if status == "announced" and listed <= frozen_now:
        problems.append("announced but already listed")
    if status in {"on-sale", "withdrawn"} and listed > frozen_now:
        problems.append("on the shelf before it was listed")
    if status == "withdrawn":
        if not withdrawn_at:
            problems.append("withdrawn without a withdrawnAt")
        elif not listed <= date.fromisoformat(withdrawn_at) <= frozen_now:
            problems.append("withdrawnAt must fall between listedAt and asOf")
    elif withdrawn_at:
        problems.append("has a withdrawnAt but is not withdrawn")

    # --- the kind names ONE block holding its details -----------------------
    # Same idea as an intent's category. An unknown productKind is allowed
    # and its block is free-form, so a new kind of product can be tried out
    # before anyone writes rules for it.
    kind = product.get("productKind")
    if kind and not isinstance(product.get(kind), dict):
        problems.append("productKind without its details block")

    # --- the rule that must never bend ----------------------------------------
    for key_path in flatten_keys(product):
        last_key = key_path.split(".")[-1]
        if last_key in FORBIDDEN_OUTCOME_KEYS:
            problems.append(f"encodes an outcome: {key_path}")
        if last_key in FORBIDDEN_CUSTOMER_KEYS:
            problems.append(f"names a customer: {key_path}")

    return problems


def insurance_product_problems(product):
    """Extra rules for a product whose productKind is 'insurance'.

    Run product_problems first; this only adds the insurance layer.
    """
    problems = []
    details = product.get("insurance") or {}

    # WHAT it covers: which dossier category, and which kinds within it.
    #   {"dossierCategory": "asset",  "kinds": ["crypto-wallet"]}
    #   {"dossierCategory": "animal", "kinds": ["horse"]}
    covers = details.get("covers") or {}
    if covers.get("dossierCategory") not in COVERABLE_DOSSIER_CATEGORIES:
        problems.append("covers.dossierCategory must be 'asset' or 'animal'")
    if not isinstance(covers.get("kinds"), list) or not covers.get("kinds"):
        problems.append("covers.kinds must list at least one kind")

    # AGAINST what. One plain-English sentence.
    if not details.get("peril"):
        problems.append("missing 'peril'")

    # HOW MUCH: a range, because one product usually serves many amounts.
    coverage = details.get("coverageUsd") or {}
    low, high = coverage.get("min"), coverage.get("max")
    if not (_is_positive_number(low) and _is_positive_number(high)):
        problems.append("coverageUsd needs a positive 'min' and 'max'")
    elif low > high:
        problems.append("coverageUsd.min is above coverageUsd.max")

    # The deductible is what the customer bears first. Zero is allowed; a
    # deductible at or above the largest payout would make the cover empty.
    deductible = details.get("deductibleUsd")
    if not isinstance(deductible, (int, float)) or isinstance(deductible, bool) or deductible < 0:
        problems.append("deductibleUsd must be zero or more")
    elif _is_positive_number(high) and deductible >= high:
        problems.append("deductibleUsd swallows the whole cover")

    # IDEA: a flat yearly premium is the simplest thing that works. A rate
    # ("1.8% of the covered amount") or a table by amount would be more
    # realistic; add "premiumRatePercent" beside this when a fixture needs it.
    if not _is_positive_number(details.get("premiumUsdPerYear")):
        problems.append("premiumUsdPerYear must be a positive number")

    term = details.get("termMonths")
    if not isinstance(term, int) or isinstance(term, bool) or term <= 0:
        problems.append("termMonths must be a positive whole number")

    # What the buyer must clear first. GENERIC check names only, and an empty
    # list is fine. This says what is ASKED, never who passed.
    requires = details.get("requires")
    if not isinstance(requires, list) or not all(isinstance(r, str) and r for r in requires):
        problems.append("'requires' must be a list of check names")

    return problems


# One checker per product kind that has rules of its own. To add a kind with
# rules: write a `<name>_product_problems(product)` function and register it.
# Kinds NOT listed here are still valid; they just get the generic rules.
PRODUCT_KIND_CHECKERS = {"insurance": insurance_product_problems}


def all_product_problems(product):
    """The full check: generic rules, plus the kind's rules if it has any."""
    problems = product_problems(product)
    kind_checker = PRODUCT_KIND_CHECKERS.get(product.get("productKind"))
    if kind_checker:
        problems += kind_checker(product)
    return problems


def load_products(folder=PRODUCTS_FOLDER):
    """Return {slug: dossier} for every product dossier in a folder.

    `folder` is a parameter so a private overlay can point this at its own
    products and reuse every rule in this file.
    """
    products = {}
    if not Path(folder).exists():
        return products
    for product_folder in sorted(Path(folder).iterdir()):
        dossier_path = product_folder / "dossier.json"
        if dossier_path.exists():
            products[product_folder.name] = json.loads(dossier_path.read_text())
    return products


def load_examples():
    """Return the worked examples from examples/catalog-examples.json."""
    return json.loads(EXAMPLES_FILE.read_text())["examples"]


def kind_of(subject):
    """The 'kind' of a dossier a product might cover.

    Assets call it assetKind ("crypto-wallet"); animals call it species
    ("horse"). This hides that difference from the matcher.
    """
    return subject.get("assetKind") or subject.get("species")


def reasons_product_does_not_fit(intent, subject, product):
    """Why this product would NOT serve this insurance wish. Empty list = it fits.

    `subject` is the dossier the wish is about (the wallet, the horse).

    THIS IS A LOOKUP, NOT A DECISION. "It fits" means only "the shelf label
    matches the ask": right kind of thing, amount in range, still on sale.
    It says nothing about whether the owner would pass any check. That stays
    the seller's job, recorded in the seller's system.
    """
    reasons = []
    details = product.get("insurance") or {}
    covers = details.get("covers") or {}

    if product.get("productKind") != "insurance":
        reasons.append("not an insurance product")
    if (product.get("availability") or {}).get("status") != "on-sale":
        reasons.append("not on sale")
    if subject.get("category") != covers.get("dossierCategory") or kind_of(subject) not in (covers.get("kinds") or []):
        reasons.append("does not cover this kind of thing")

    wanted = (intent.get("insurance") or {}).get("coverageUsd")
    coverage = details.get("coverageUsd") or {}
    if isinstance(wanted, (int, float)) and coverage:
        if wanted < coverage.get("min", 0):
            reasons.append("asks for less than the product's minimum")
        if wanted > coverage.get("max", float("inf")):
            reasons.append("asks for more than the product's maximum")
    return reasons


def products_that_fit(intent, subject, products):
    """Slugs of every product on the shelf that could serve this wish.

    This is "the wish meets the shelf". It works the same for a wallet, a
    horse or a farmhouse, which is the point: one matcher, many stores.
    An empty list is a real and useful answer ("nobody sells this").
    """
    return [
        slug for slug, product in sorted(products.items())
        if product.get("honesty", {}).get("role") != "VILLAIN"
        and not reasons_product_does_not_fit(intent, subject, product)
    ]


def named_product_notes(intent, subject, products):
    """Check a wish that NAMES a product (insurance.productSlug is optional).

    Returns (problems, mismatches):
      problems    the fixture itself is broken: it points at a product that
                  does not exist. Tests fail on these.
      mismatches  the fixture is fine but the ASK does not fit the product:
                  wrong amount, withdrawn, wrong kind of thing. These are
                  deliberate and useful. People really do ask for the wrong
                  product; a consumer has to cope, so the town shows it.
    """
    slug = (intent.get("insurance") or {}).get("productSlug")
    if slug is None:
        return [], []                       # a product-blind wish: nothing to check
    if slug not in products:
        return [f"names a product that does not exist: {slug}"], []
    return [], reasons_product_does_not_fit(intent, subject, products[slug])


def main():
    # Imported here, not at the top, so this file stays usable on its own
    # (a private overlay may have products but no asset dossiers).
    from validate_intents import load_asset_dossiers

    failures = 0
    products = load_products()

    print("Products on TestTown's shelves:")
    for slug, product in products.items():
        problems = all_product_problems(product)
        failures += bool(problems)
        status = (product.get("availability") or {}).get("status", "?")
        verdict = "ok" if not problems else "PROBLEM: " + "; ".join(problems)
        print(f"  {slug[:52]:52} {status:10} {verdict}")

    print("\nInsurance wishes meeting the shelf (a lookup, not a decision):")
    for slug, asset in load_asset_dossiers():
        for intent in asset.get("intents", []):
            if intent.get("category") != "insurance" or intent["status"] != "open":
                continue
            problems, mismatches = named_product_notes(intent, asset, products)
            failures += bool(problems)
            named = intent["insurance"].get("productSlug")
            fits = products_that_fit(intent, asset, products)
            line = f"  {slug:26} ${intent['insurance']['coverageUsd']:>6,}  fits: {', '.join(fits) or 'NOTHING ON THE SHELF'}"
            if named:
                line += f"\n  {'':26}          named {named}: {'; '.join(problems + mismatches) or 'fits'}"
            print(line)

    print("\nWorked examples (some are broken on purpose):")
    for example in load_examples():
        problems = all_product_problems(example["product"])
        behaved_as_documented = (not problems) == example["expectValid"]
        failures += not behaved_as_documented
        label = "valid" if not problems else "rejected: " + "; ".join(problems)
        flag = "" if behaved_as_documented else "   <-- NOT what the example says"
        print(f"  {example['id']:40} {label}{flag}")

    print("\nAll good." if not failures else f"\n{failures} thing(s) need attention.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
