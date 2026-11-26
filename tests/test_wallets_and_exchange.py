"""Checks for operator wallets and the exchange.

Three promises are tested here:
  1. Everyone who should have a wallet has one, and nobody who should not
     (the convention fixtures) has one.
  2. Only PUBLIC halves are in the repo. A seed can never be committed
     without this file failing.
  3. The exchange's multi-sig wallets are honest about what is real (the
     signer addresses) and what is a placeholder (the multi-sig account).
"""

from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / "dossiers"
ASSIGNMENTS = json.loads((ROOT / "tools" / "wallet-assignments.json").read_text())["wallets"]

# What a Midnight pre-prod unshielded address looks like.
PREPROD_ADDRESS = re.compile(r"^mn_addr_preprod1[a-z0-9]{40,}$")
# A 32-byte seed is 64 hex characters. Nothing in this repo should look like one
# sitting under a key that names it.
SECRET_KEYS = {"seed", "seedPhrase", "mnemonic", "privateKey", "secretKey"}

EXCHANGE = "quarry-street-exchange"


def load(category):
    for folder in sorted((DOSSIERS / category).iterdir()):
        path = folder / "dossier.json"
        if path.exists():
            yield json.loads(path.read_text())


def all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from all_keys(value)
    elif isinstance(node, list):
        for value in node:
            yield from all_keys(value)


class OperatorWalletTests(unittest.TestCase):
    def test_every_resident_citizen_and_organization_has_an_address(self):
        for category in ("citizens", "organizations"):
            for dossier in load(category):
                if dossier["slug"].startswith("convention-"):
                    continue
                address = dossier["operator"].get("preprodAddress")
                self.assertRegex(address or "", PREPROD_ADDRESS, dossier["slug"])
                self.assertTrue(dossier["operator"].get("walletCard"), dossier["slug"])

    def test_convention_fixtures_have_no_wallet(self):
        # Their own projection test forbids a key; keep the two in step.
        for category in ("citizens", "organizations"):
            for dossier in load(category):
                if dossier["slug"].startswith("convention-"):
                    self.assertNotIn("preprodAddress", dossier["operator"], dossier["slug"])

    def test_dossier_addresses_match_the_assignment_file(self):
        for category in ("citizens", "organizations"):
            for dossier in load(category):
                if dossier["slug"] in ASSIGNMENTS:
                    self.assertEqual(dossier["operator"]["preprodAddress"],
                                     ASSIGNMENTS[dossier["slug"]]["preprodAddress"], dossier["slug"])

    def test_assigned_addresses_are_well_formed_and_never_reused(self):
        addresses = [w["preprodAddress"] for w in ASSIGNMENTS.values()]
        for address in addresses:
            self.assertRegex(address, PREPROD_ADDRESS)
        self.assertEqual(len(addresses), len(set(addresses)))

    def test_no_secret_is_committed(self):
        for category in ("citizens", "organizations", "assets", "animals"):
            for dossier in load(category):
                for key in all_keys(dossier):
                    self.assertNotIn(key, SECRET_KEYS, dossier["slug"])
        self.assertFalse(set(all_keys(ASSIGNMENTS)) & SECRET_KEYS)
        # No seed files anywhere in the repo.
        self.assertEqual([p for p in ROOT.rglob("*.seed") if ".git" not in p.parts], [])


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.orgs = {d["slug"]: d for d in load("organizations")}
        self.assets = {d["slug"]: d for d in load("assets")}
        self.citizens = {d["slug"]: d for d in load("citizens")}
        self.exchange = self.orgs[EXCHANGE]["exchange"]
        self.known_addresses = {w["preprodAddress"] for w in ASSIGNMENTS.values()}

    def test_exchange_is_an_authentic_registered_organization(self):
        dossier = self.orgs[EXCHANGE]
        self.assertEqual(dossier["honesty"]["role"], "AUTHENTIC")
        eins = json.loads((ROOT / "registries/irs-ein-registry.json").read_text())["eins"]
        regs = json.loads((ROOT / "registries/state-corporations-registry.json").read_text())["registrations"]
        self.assertIn(dossier["identifiers"]["ein"], eins)
        self.assertIn(dossier["identifiers"]["stateRegistration"], regs)

    def test_exchange_points_at_wallets_that_exist(self):
        self.assertEqual(len(self.exchange["corporateWallets"]), 1)
        self.assertGreaterEqual(len(self.exchange["customerWallets"]), 1)
        for slug in self.exchange["corporateWallets"]:
            self.assertEqual(self.assets[slug]["ownerOrganizationSlug"], EXCHANGE)
        for slug in self.exchange["customerWallets"]:
            wallet = self.assets[slug]
            self.assertEqual(wallet["custodianOrganizationSlug"], EXCHANGE)
            customer = wallet["ownerCitizenSlug"]
            self.assertIn(customer, self.exchange["customers"])
            self.assertIn(slug, self.citizens[customer]["householdSlugs"]["assets"])

    def test_multisig_wallets_are_sound(self):
        for slug in self.exchange["corporateWallets"] + self.exchange["customerWallets"]:
            custody = self.assets[slug]["custody"]
            self.assertEqual(custody["model"], "multi-sig", slug)
            self.assertEqual(custody["signerCount"], len(custody["signers"]), slug)
            # More than one signer needed, and never more than exist.
            self.assertGreater(custody["threshold"], 1, slug)
            self.assertLessEqual(custody["threshold"], custody["signerCount"], slug)
            signer_addresses = [s["preprodAddress"] for s in custody["signers"]]
            self.assertEqual(len(signer_addresses), len(set(signer_addresses)), slug)
            for address in signer_addresses:
                self.assertIn(address, self.known_addresses, slug)

    def test_customer_cannot_be_locked_out_and_exchange_cannot_act_alone(self):
        template = self.exchange["customerWalletTemplate"]
        for slug in self.exchange["customerWallets"]:
            wallet = self.assets[slug]
            custody = wallet["custody"]
            roles = [s["role"] for s in custody["signers"]]
            self.assertEqual(sorted(roles), sorted(template["signerRoles"]), slug)
            self.assertEqual(custody["threshold"], template["threshold"], slug)
            # The customer signs with their own operator key.
            customer_address = self.citizens[wallet["ownerCitizenSlug"]]["operator"]["preprodAddress"]
            by_role = {s["role"]: s["preprodAddress"] for s in custody["signers"]}
            self.assertEqual(by_role["customer"], customer_address, slug)
            # The trustee is independent of the exchange.
            trustee = self.orgs[template["recoveryTrusteeOrganizationSlug"]]
            self.assertNotEqual(trustee["slug"], EXCHANGE)
            self.assertEqual(by_role["recovery-trustee"], trustee["operator"]["preprodAddress"], slug)
            exchange_keys = sum(role == "exchange-cosigner" for role in roles)
            self.assertLess(exchange_keys, custody["threshold"], slug)

    def test_placeholders_are_declared_not_hidden(self):
        for slug in self.exchange["corporateWallets"] + self.exchange["customerWallets"]:
            wallet = self.assets[slug]
            # The account address is not known yet, and says so.
            self.assertIsNone(wallet["identityAnchor"]["value"], slug)
            self.assertEqual(wallet["identityAnchor"]["status"], "PLACEHOLDER", slug)
            self.assertIsNone(wallet["holdings"]["balanceUsd"], slug)
            fields = {p["field"] for p in wallet["placeholders"]}
            self.assertIn("identityAnchor.value", fields, slug)
            self.assertIn("holdings.balanceUsd", fields, slug)
            for placeholder in wallet["placeholders"]:
                self.assertEqual(placeholder["status"], "PLACEHOLDER", slug)
                self.assertTrue(placeholder["reason"] and placeholder["unblockedBy"], slug)


if __name__ == "__main__":
    unittest.main()
