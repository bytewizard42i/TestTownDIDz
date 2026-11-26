"""Checks for the corporate multisig pool: variable corporate assets.

The pool is four multi-signature wallet fixtures (2-of-2, 2-of-3, 3-of-5,
4-of-7) owned by NO organization — spare parts a test assigns to any
corporate object that needs that shape. The promises tested here:

  1. All four fixtures exist, in the registry AND as asset dossiers, with
     the right signer counts and thresholds.
  2. Every signer key is a real published pre-prod address (public half
     only — seeds never enter this repo).
  3. No signer key collides with a roster name: operators are never test
     subjects (docs/SECRETS_CONVENTION.md).
  4. The fixtures are honest placeholders: the multi-sig account does not
     exist yet and says so, exactly like the exchange's wallets.
"""

from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "registries" / "corporate-multisig-pool.json").read_text())
ASSIGNMENTS = json.loads((ROOT / "tools" / "wallet-assignments.json").read_text())["wallets"]
PREPROD_ADDRESS = re.compile(r"^mn_addr_preprod1[a-z0-9]{40,}$")

# The four shapes the pool must hold. The same table lives in
# tools/generate_population.py (the source of truth) and in the private
# vault tool; this expectation is the test-side pin.
EXPECTED_SHAPES = {
    "tiny-corp-multisig":  (2, 2),
    "med-corp-multisig":   (3, 2),
    "big-corp-multisig":   (5, 3),
    "giant-corp-multisig": (7, 4),
}


def roster_names():
    text = (ROOT / "tools" / "generate_population.py").read_text()
    block = re.search(r"LADIES = \{(.*?)\n\}", text, re.S).group(1)
    return set(re.findall(r'"(\w+)":\s*"mn_addr', block))


class CorporateMultisigPoolTests(unittest.TestCase):
    def setUp(self):
        self.pool = {entry["slug"]: entry for entry in REGISTRY["pool"]}
        self.dossiers = {}
        for slug in EXPECTED_SHAPES:
            path = ROOT / "dossiers" / "assets" / slug / "dossier.json"
            if path.exists():
                self.dossiers[slug] = json.loads(path.read_text())

    def test_all_four_shapes_exist_with_correct_signer_counts_and_thresholds(self):
        self.assertEqual(sorted(self.pool), sorted(EXPECTED_SHAPES))
        for slug, (signers, threshold) in EXPECTED_SHAPES.items():
            entry = self.pool[slug]
            self.assertEqual(entry["signerCount"], signers, slug)
            self.assertEqual(entry["threshold"], threshold, slug)
            self.assertEqual(len(entry["signers"]), signers, slug)

    def test_every_fixture_has_a_dossier_that_agrees_with_the_registry(self):
        for slug, (signers, threshold) in EXPECTED_SHAPES.items():
            self.assertIn(slug, self.dossiers, f"{slug}: no asset dossier")
            dossier = self.dossiers[slug]
            self.assertEqual(dossier["category"], "asset", slug)
            self.assertEqual(dossier["assetKind"], "crypto-wallet", slug)
            custody = dossier["custody"]
            self.assertEqual(custody["model"], "multi-sig", slug)
            self.assertEqual(custody["signerCount"], signers, slug)
            self.assertEqual(custody["threshold"], threshold, slug)
            self.assertEqual(len(custody["signers"]), signers, slug)
            registry_keys = [s["keySlug"] for s in self.pool[slug]["signers"]]
            dossier_keys = [f"{slug}--signer-{i}" for i in range(1, signers + 1)]
            self.assertEqual(registry_keys, dossier_keys, slug)

    def test_signer_keys_are_published_public_halves_and_never_reused(self):
        all_addresses = []
        for slug in EXPECTED_SHAPES:
            for signer in self.pool[slug]["signers"]:
                key = signer["keySlug"]
                self.assertIn(key, ASSIGNMENTS, key)
                self.assertEqual(ASSIGNMENTS[key]["kind"], "multisig-pool-signer", key)
                self.assertEqual(ASSIGNMENTS[key]["preprodAddress"], signer["preprodAddress"], key)
                self.assertRegex(signer["preprodAddress"], PREPROD_ADDRESS, key)
                # The pseudonym is the lowercase display form: slug plus address tag.
                tag = signer["preprodAddress"].replace("mn_addr_preprod1", "")[:6]
                self.assertEqual(signer["pseudonym"], f"{key}-addr{tag}", key)
                all_addresses.append(signer["preprodAddress"])
        self.assertEqual(len(all_addresses), 17)
        self.assertEqual(len(set(all_addresses)), 17, "two signer keys share an address")

    def test_no_signer_key_collides_with_a_roster_name(self):
        roster = roster_names()
        self.assertEqual(len(roster), 20)
        for signer_key in self.pool_signer_keys():
            self.assertNotIn(signer_key, roster)
            first_word = signer_key.split("-")[0]
            self.assertNotIn(first_word, roster,
                             f"{signer_key}'s first word collides with roster wallet '{first_word}'")
        # The fixtures themselves may not use a roster name either.
        for slug in EXPECTED_SHAPES:
            self.assertNotIn(slug, roster)

    def pool_signer_keys(self):
        return [s["keySlug"] for entry in self.pool.values() for s in entry["signers"]]

    def test_fixtures_are_unowned_variable_assets(self):
        for slug in EXPECTED_SHAPES:
            dossier = self.dossiers[slug]
            # No owner of either kind: a pool fixture belongs to nobody
            # until a test assigns it.
            self.assertNotIn("ownerCitizenSlug", dossier, slug)
            self.assertNotIn("ownerOrganizationSlug", dossier, slug)
            pool_block = dossier["fixturePool"]
            self.assertEqual(pool_block["pool"], "corporate-multisig", slug)
            self.assertIsNone(pool_block["ownedBy"], slug)
            self.assertEqual(pool_block["status"],
                             "placeholder: requires multisig contract deployment", slug)

    def test_fixtures_are_honest_placeholders(self):
        for slug in EXPECTED_SHAPES:
            dossier = self.dossiers[slug]
            self.assertIsNone(dossier["identityAnchor"]["value"], slug)
            self.assertEqual(dossier["identityAnchor"]["status"], "PLACEHOLDER", slug)
            self.assertIsNone(dossier["holdings"]["balanceUsd"], slug)
            fields = {p["field"] for p in dossier["placeholders"]}
            self.assertIn("identityAnchor.value", fields, slug)
            for entry in self.pool.values():
                self.assertEqual(entry["status"],
                                 "placeholder: requires multisig contract deployment")

    def test_registry_signers_match_the_dossier_signers(self):
        for slug in EXPECTED_SHAPES:
            dossier_addresses = [s["preprodAddress"] for s in self.dossiers[slug]["custody"]["signers"]]
            registry_addresses = [s["preprodAddress"] for s in self.pool[slug]["signers"]]
            self.assertEqual(dossier_addresses, registry_addresses, slug)


if __name__ == "__main__":
    unittest.main()
