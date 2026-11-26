"""Validate the intents layer: the rules, in one importable place.

WHAT THIS IS
    An "intent" is a WANT that somebody in TestTown has voiced about an
    asset: "sell the piano", "lend the van", "insure this wallet for $500".
    This module holds the rules that decide whether an intent is well formed.
    The tests import it, and you can run it by hand:

        python3 tools/validate_intents.py

    That checks every asset dossier and every worked example and prints what
    it found. Exit code 0 means everything is fine; 1 means something is off.

WHY THE RULES LIVE HERE AND NOT IN THE TESTS
    Any consumer of TestTown (CryptoSure today, others later) needs the same
    answer to "is this intent usable?". Keeping the rules in a tool means a
    consumer can copy or port one small file instead of reading test code.

THE TWO LEVELS (read docs/INTENTS_LAYER.md for the long version)
    1. GENERIC INTENT   -- can be about anything. Three required fields.
    2. INSURANCE WISH   -- a generic intent whose category is "insurance",
                           with stricter rules on top.

THE ONE RULE THAT MUST NEVER BEND
    Intents are wants, never outcomes. TestTown is "the world BEFORE the
    trust system". Whether Bonnie passes KYC, or whether a policy was bound,
    is decided by gatekeepers (oracles, registries, contracts) and recorded
    by THEM. If an intent ever carried "approved": true, every consumer would
    be tempted to trust the fixture instead of doing its own check.
"""

from datetime import date
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS_FOLDER = ROOT / "dossiers" / "assets"
EXAMPLES_FILE = ROOT / "examples" / "intents-examples.json"

# The four stages an intent can be frozen at.
#   open       a live ask, waiting for an answer
#   accepted   the OWNER took an offer (the owner's act, not a gate verdict)
#   withdrawn  the owner changed their mind
#   expired    nobody answered before expiresAt; kept as history
# IDEA: "superseded" (replaced by a newer intent) and "paused" could join
# this list once a fixture needs them. Add the status here, add an example,
# and the tests will tell you what else has to change.
VALID_INTENT_STATUSES = {"open", "accepted", "withdrawn", "expired"}

# Field names that would smuggle a gate's decision into a want. This list is
# deliberately blunt: it is cheaper to rename a harmless field than to let
# one outcome leak into the population.
FORBIDDEN_OUTCOME_KEYS = {
    "outcome", "approved", "declined", "pass", "fail",
    "kycLevel", "kycPassed", "geoPassed", "screeningResult", "bound",
}

# Insurance wishes we know how to read. Only one so far.
# IDEA: "raise-cover", "lower-cover", "renew-cover", "cancel-cover" and
# "add-beneficiary" are the obvious next wishes. Each would likely need its
# own fields (for example the policy being changed), so add them one at a
# time, with an example, rather than opening this up to any string.
KNOWN_INSURANCE_WISHES = {"cover-asset"}


def flatten_keys(node, prefix=""):
    """Yield every key path inside nested dicts and lists, e.g. 'insurance.wish'."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield prefix + key
            yield from flatten_keys(value, prefix + key + ".")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from flatten_keys(value, f"{prefix}{index}.")


def generic_intent_problems(intent, frozen_now):
    """Check the rules EVERY intent obeys. Returns a list of problem strings.

    An empty list means the intent is fine. We return problems instead of
    raising so a caller can show all of them at once.

    frozen_now is "today" for the fixture. Fixtures are frozen in time, so we
    never use the real clock: an intent that is open in the fixture must stay
    open no matter when the tests run. For a wallet, frozen_now is the
    asset's holdings.asOf date.
    """
    problems = []

    # --- the three required fields ---------------------------------------
    if not intent.get("wants"):
        problems.append("missing 'wants'")
    if intent.get("status") not in VALID_INTENT_STATUSES:
        problems.append("bad status")
    if "expressedAt" not in intent:
        # Without this date none of the date checks below can run.
        return problems + ["missing 'expressedAt'"]

    # --- the lifecycle: expressedAt -> startDate -> expiresAt -------------
    expressed = date.fromisoformat(intent["expressedAt"])
    if expressed > frozen_now:
        problems.append("expressed in the future")

    # startDate is optional: "when should this take effect?"
    if "startDate" in intent and date.fromisoformat(intent["startDate"]) < expressed:
        problems.append("starts before it was expressed")

    # expiresAt is optional: "after this, stop treating it as a live ask".
    # It MAY fall before startDate (offer open to Dec 31 for a Jan 1 start).
    if "expiresAt" in intent:
        expires = date.fromisoformat(intent["expiresAt"])
        if expires <= expressed:
            problems.append("expires before it was expressed")
        if intent.get("status") == "open" and expires < frozen_now:
            problems.append("open but already stale")
        if intent.get("status") == "expired" and expires >= frozen_now:
            problems.append("marked expired too early")
    elif intent.get("status") == "expired":
        problems.append("expired without an expiresAt")

    # --- the optional category ---------------------------------------------
    # A category names ONE extra block that holds its details. An unknown
    # category is allowed and its block is free-form: that is what keeps the
    # generic intent open to anything.
    if "category" in intent and not isinstance(intent.get(intent["category"]), dict):
        problems.append("category without its details block")

    # --- the rule that must never bend --------------------------------------
    for key_path in flatten_keys(intent):
        if key_path.split(".")[-1] in FORBIDDEN_OUTCOME_KEYS:
            problems.append(f"encodes an outcome: {key_path}")

    return problems


def insurance_wish_problems(intent):
    """Extra rules for an intent whose category is 'insurance'.

    Run generic_intent_problems first; this only adds the insurance layer.
    An insurer cannot quote an open-ended ask, so both dates are required.
    """
    problems = [
        f"missing '{field}'" for field in ("startDate", "expiresAt") if field not in intent
    ]
    details = intent.get("insurance", {})
    if details.get("wish") not in KNOWN_INSURANCE_WISHES:
        problems.append("unknown insurance wish")

    # coverageUsd is what the owner ASKED for. It is allowed to be far above
    # or below the balance: people over-insure and under-insure on purpose,
    # and that mismatch is useful demo material (a sizing conversation).
    # IDEA: add "currency" beside the amount when a non-USD town appears.
    coverage = details.get("coverageUsd")
    if not isinstance(coverage, (int, float)) or coverage <= 0:
        problems.append("coverageUsd must be a positive number")

    # productSlug is OPTIONAL: the owner may name the exact product they want
    # ("the Plus one"), or leave it out and stay product-blind. Here we only
    # check its shape. Whether that product exists, and whether the ask fits
    # it, is checked against the catalog in tools/validate_catalog.py, so
    # this file never needs to know what is on the shelf.
    if "productSlug" in details and not (
        isinstance(details["productSlug"], str) and details["productSlug"]
    ):
        problems.append("productSlug must be a non-empty string when present")
    return problems


# One checker per category that has rules of its own. To add a category with
# rules: write a `<name>_problems(intent)` function and register it here.
# Categories NOT listed here are still valid; they just get the generic rules.
CATEGORY_CHECKERS = {"insurance": insurance_wish_problems}


def all_intent_problems(intent, frozen_now):
    """The full check: generic rules, plus the category's rules if it has any."""
    problems = generic_intent_problems(intent, frozen_now)
    category_checker = CATEGORY_CHECKERS.get(intent.get("category"))
    if category_checker:
        problems += category_checker(intent)
    return problems


def load_asset_dossiers():
    """Yield (slug, dossier) for every asset dossier on disk."""
    for folder in sorted(ASSETS_FOLDER.iterdir()):
        dossier_path = folder / "dossier.json"
        if dossier_path.exists():
            yield folder.name, json.loads(dossier_path.read_text())


def load_examples():
    """Return the worked examples from examples/intents-examples.json."""
    return json.loads(EXAMPLES_FILE.read_text())["examples"]


def main():
    failures = 0

    print("Asset dossiers carrying intents:")
    for slug, dossier in load_asset_dossiers():
        for intent in dossier.get("intents", []):
            frozen_now = date.fromisoformat(dossier["holdings"]["asOf"])
            problems = all_intent_problems(intent, frozen_now)
            failures += bool(problems)
            verdict = "ok" if not problems else "PROBLEM: " + "; ".join(problems)
            print(f"  {slug:28} {intent['status']:9} {intent['wants'][:38]:38} {verdict}")

    print("\nWorked examples (some are broken on purpose):")
    for example in load_examples():
        problems = all_intent_problems(example["intent"], date.fromisoformat(example["frozenNow"]))
        behaved_as_documented = (not problems) == example["expectValid"]
        failures += not behaved_as_documented
        label = "valid" if not problems else "rejected: " + "; ".join(problems)
        flag = "" if behaved_as_documented else "   <-- NOT what the example says"
        print(f"  {example['id']:38} {label}{flag}")

    print("\nAll good." if not failures else f"\n{failures} thing(s) need attention.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
