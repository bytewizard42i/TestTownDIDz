"""Integrity and privacy-boundary checks for fictional convention fixtures."""

from pathlib import Path
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools/generate_convention_projection.py"
SPEC = importlib.util.spec_from_file_location("convention_generator", GENERATOR_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)
PROJECTION_PATH = ROOT / "projections/eventrevolution/convention-v1.json"


class ConventionProjectionTests(unittest.TestCase):
    def setUp(self):
        self.projection = json.loads(PROJECTION_PATH.read_text())

    def test_explicit_fictional_evidence_and_expected_inventory(self):
        self.assertEqual(self.projection["schema"], "testtown/eventrevolution-convention/v1")
        self.assertEqual(self.projection["eventId"], "demo-convention-2026")
        self.assertEqual(self.projection["evidence"], "MOCK")
        self.assertIs(self.projection["fictional"], True)
        self.assertEqual(len(self.projection["people"]), 12)
        self.assertEqual(len(self.projection["organizations"]), 4)
        self.assertEqual(len(self.projection["kiosks"]), 4)
        self.assertEqual(len(self.projection["deviceTwins"]), 9)
        self.assertEqual({person["role"] for person in self.projection["people"]}, {"enthusiast", "developer", "founder", "worker"})

    def test_identifiers_are_unique_and_venue_geometry_is_not_duplicated(self):
        for collection in ["venues", "people", "organizations", "kiosks", "deviceTwins", "assignments"]:
            identifiers = [record["id"] for record in self.projection[collection]]
            self.assertEqual(len(identifiers), len(set(identifiers)), collection)
        self.assertEqual({venue["id"] for venue in self.projection["venues"]}, {"studio-hall", "split-level", "three-building-campus"})
        for venue in self.projection["venues"]:
            self.assertEqual(set(venue), {"id", "name", "description", "layoutKind"})

    def test_profile_privacy_states_are_internally_consistent(self):
        expected_flags = {"discoverable", "matching", "locationSharing", "availabilitySharing", "paused"}
        allowed_slots = {"privacy", "mingle", "future", "food"}
        for person in self.projection["people"]:
            flags = person["consent"]
            self.assertEqual(set(flags), expected_flags)
            self.assertTrue(all(type(value) is bool for value in flags.values()))
            self.assertIn(person["availability"], {"open-to-meet", "busy", "unavailable", "unknown"})
            if flags["paused"]:
                self.assertFalse(any(flags[key] for key in expected_flags - {"paused"}))
            if not flags["locationSharing"]:
                self.assertNotIn("presenceSlot", person)
            elif "presenceSlot" in person:
                self.assertIn(person["presenceSlot"], allowed_slots)
            if not flags["availabilitySharing"] and not flags["paused"]:
                self.assertEqual(person["availability"], "unknown")

    def test_all_cross_references_resolve_without_owning_people(self):
        people = {person["id"]: person for person in self.projection["people"]}
        companies = {company["id"]: company for company in self.projection["organizations"]}
        kiosks = {kiosk["id"]: kiosk for kiosk in self.projection["kiosks"]}
        devices = {device["id"]: device for device in self.projection["deviceTwins"]}
        venues = {venue["id"] for venue in self.projection["venues"]}
        for person in people.values():
            if "companyId" in person:
                self.assertIn(person["companyId"], companies)
            self.assertTrue(set(person["venueIds"]).issubset(venues))
            dossier = json.loads((ROOT / "dossiers/citizens" / person["dossierSlug"] / "dossier.json").read_text())
            self.assertEqual(dossier["category"], "citizen")
            self.assertNotIn("ownerCitizenSlug", dossier)
            self.assertNotIn("ownerOrganizationSlug", dossier)
        self.assertEqual({kiosk["destinationSlot"] for kiosk in kiosks.values()}, {"privacy", "mingle", "future", "food"})
        for kiosk in kiosks.values():
            self.assertIn(kiosk["companyId"], companies)
            self.assertTrue(set(kiosk["venueIds"]).issubset(venues))
            for worker_id in kiosk["workerIds"]:
                self.assertIn(worker_id, people)
                self.assertEqual(people[worker_id]["companyId"], kiosk["companyId"])
        assigned_devices = []
        for assignment in self.projection["assignments"]:
            self.assertEqual(assignment["eventId"], self.projection["eventId"])
            self.assertIn(assignment["deviceId"], devices)
            assigned_devices.append(assignment["deviceId"])
            self.assertNotEqual("profileId" in assignment, "kioskId" in assignment)
            if "profileId" in assignment:
                self.assertIn(assignment["profileId"], people)
            if "kioskId" in assignment:
                self.assertIn(assignment["kioskId"], kiosks)
            self.assertNotIn("ownershipTransfer", assignment)
        self.assertEqual(len(assigned_devices), len(set(assigned_devices)))

    def test_every_new_dossier_has_valid_fictional_evidence(self):
        for relative in GENERATOR.build_files():
            if not relative.endswith("/dossier.json"):
                continue
            path = ROOT / relative
            dossier = json.loads(path.read_text())
            self.assertEqual(dossier["schema"], "testtown/dossier/v0.1")
            self.assertEqual(dossier["evidence"], "MOCK")
            self.assertIs(dossier["fictional"], True)
            self.assertTrue(dossier["documents"])
            for document in dossier["documents"]:
                content = (path.parent / document["file"]).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), document["sha256"])
                self.assertIn(b"Evidence: MOCK", content)
                self.assertTrue((ROOT / document["confirmableBy"]).is_file())

    def test_participation_does_not_admit_trusted_issuers(self):
        registry = json.loads((ROOT / "registries/convention-participation-registry.json").read_text())
        for company in self.projection["organizations"]:
            self.assertIn(company["dossierSlug"], registry["organizations"])
            dossier = json.loads((ROOT / "dossiers/organizations" / company["dossierSlug"] / "dossier.json").read_text())
            self.assertEqual(dossier["participation"]["issuerAdmission"], "not-requested")
            self.assertIs(dossier["participation"]["trustedIssuer"], False)
            self.assertNotIn("ein", dossier["identifiers"])
            self.assertNotIn("preprodAddress", dossier["operator"])

    def test_device_twins_preserve_radio_and_timestamp_limits(self):
        for device in self.projection["deviceTwins"]:
            self.assertEqual(device["evidence"], "MOCK")
            self.assertTrue(device["inventoryIdentifier"].startswith("TT-CONV-"))
            self.assertFalse(device["capabilities"]["measuresDistance"])
            self.assertFalse(device["capabilities"]["suppliesTrustedLocation"])
            self.assertFalse(device["capabilities"]["votesInConsensus"])
            if device["kind"] == "bc021-tag":
                self.assertFalse(device["capabilities"]["scansTags"])
            else:
                self.assertEqual(device["measurementFreshness"], "unknown")
                self.assertIsNone(device["measurementTimestampMs"])
            self.assertNotIn("qrPayload", device)
            self.assertNotIn("serialNumber", device)

    def test_adversarial_twins_are_excluded_from_authentic_inventory(self):
        registry = json.loads((ROOT / "registries/convention-participation-registry.json").read_text())
        villains = list((ROOT / "dossiers/assets").glob("VILLAIN--convention-*/dossier.json"))
        self.assertEqual(len(villains), 2)
        for path in villains:
            dossier = json.loads(path.read_text())
            self.assertEqual(dossier["honesty"]["role"], "VILLAIN")
            self.assertNotIn(dossier["slug"], registry["assets"])
            self.assertNotIn("ownerCitizenSlug", dossier)
            self.assertNotIn("ownerOrganizationSlug", dossier)
        clone = json.loads(next(path for path in villains if "copied-label" in str(path)).read_text())
        self.assertEqual(clone["identityAnchor"]["value"], self.projection["deviceTwins"][0]["inventoryIdentifier"])

    def test_generated_bytes_match_committed_projection_and_dossiers(self):
        for relative, expected in GENERATOR.build_files().items():
            self.assertEqual((ROOT / relative).read_bytes(), expected.encode("utf-8"), relative)

    def test_generator_refuses_to_overwrite_existing_content_before_any_writes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            projection = temporary_root / "projections/eventrevolution/convention-v1.json"
            projection.parent.mkdir(parents=True)
            projection.write_text("PRESERVE THIS EXISTING CONTENT")
            with patch.object(GENERATOR, "ROOT", temporary_root), patch.object(sys, "argv", ["generator"]):
                with self.assertRaises(SystemExit):
                    GENERATOR.main()
            self.assertEqual(projection.read_text(), "PRESERVE THIS EXISTING CONTENT")
            self.assertFalse((temporary_root / "dossiers").exists())

    def test_check_mode_is_read_only_when_files_are_missing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            with patch.object(GENERATOR, "ROOT", temporary_root), patch.object(sys, "argv", ["generator", "--check"]):
                with self.assertRaises(SystemExit):
                    GENERATOR.main()
            self.assertEqual(list(temporary_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
