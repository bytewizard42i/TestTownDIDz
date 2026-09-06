#!/usr/bin/env python3
"""Build fictional convention dossiers and their reusable event projection.

This generator never changes pre-existing bytes. Matching files are left alone;
drift is an error. Use --check for read-only reproducibility validation. Existing
population and government-registry generators remain independent and untouched.
"""

from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
EVENT_ID = "demo-convention-2026"
PROJECTION_PATH = "projections/eventrevolution/convention-v1.json"
VENUE_IDS = ["studio-hall", "split-level", "three-building-campus"]
REGISTRY_PATH = "registries/convention-participation-registry.json"
DATASET_ID = "testtown-convention-2026-09-06"


def encoded_json(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def consent(discoverable=True, matching=True, location=True, availability=True, paused=False):
    return {
        "discoverable": discoverable,
        "matching": matching,
        "locationSharing": location,
        "availabilitySharing": availability,
        "paused": paused,
    }


def convention_data():
    venues = [
        {"id": "studio-hall", "name": "TestTown Studio Hall", "layoutKind": "single-level",
         "description": "Fictional single-level convention hall with a main exhibition area and peripheral meeting rooms. Geometry belongs to the consuming venue adapter."},
        {"id": "split-level", "name": "TestTown Terrace Forum", "layoutKind": "split-level",
         "description": "Fictional two-floor convention venue with a halfway VIP (Very Important Person) lounge between the principal floors. Geometry belongs to the consuming venue adapter."},
        {"id": "three-building-campus", "name": "TestTown Lantern Campus", "layoutKind": "three-building-campus",
         "description": "Fictional main convention building and two satellite buildings connected by outdoor walkways. Geometry belongs to the consuming venue adapter."},
    ]

    organizations = [
        {"id": "lanternmoss-proofworks", "dossierSlug": "convention-lanternmoss-proofworks", "name": "LanternMoss Proofworks", "kind": "crypto-company",
         "description": "Fictional developer tools company exploring selective disclosure and privacy-preserving proofs.", "interests": ["selective privacy", "zero-knowledge proofs", "developer tooling"]},
        {"id": "copperkite-wallet-studio", "dossierSlug": "convention-copperkite-wallet-studio", "name": "CopperKite Wallet Studio", "kind": "crypto-company",
         "description": "Fictional wallet company exploring accessible onboarding and participant-controlled connections.", "interests": ["wallets", "accessibility", "professional networking"]},
        {"id": "prismsprout-infrastructure", "dossierSlug": "convention-prismsprout-infrastructure", "name": "PrismSprout Infrastructure", "kind": "crypto-company",
         "description": "Fictional infrastructure company exploring device identity, asset provenance, and resilient event tools.", "interests": ["device identity", "asset provenance", "offline resilience"]},
        {"id": "sunnyorchard-kitchen", "dossierSlug": "convention-sunnyorchard-kitchen", "name": "SunnyOrchard Kitchen", "kind": "food-vendor",
         "description": "Fictional convention food vendor serving coffee, fruit bowls, and simple dietary options.", "interests": ["food", "coffee", "dietary accessibility"]},
    ]

    # These biographies are invented for product rehearsal, not scraped profiles.
    people = [
        {"id": "avery-bloom", "displayName": "Avery Bloom", "role": "enthusiast", "biography": "A fictional first-time convention visitor learning how selective privacy can improve everyday apps.", "interests": ["selective privacy", "wallets", "meeting builders"], "availability": "open-to-meet", "presenceSlot": "privacy", "consent": consent()},
        {"id": "elio-reed", "displayName": "Elio Reed", "role": "enthusiast", "biography": "A fictional community organizer interested in accessible onboarding and thoughtful professional connections.", "interests": ["accessibility", "professional networking", "community"], "availability": "open-to-meet", "presenceSlot": "mingle", "consent": consent()},
        {"id": "june-alder", "displayName": "June Alder", "role": "enthusiast", "biography": "A fictional attendee comparing independent hardware projects and taking a private break from discovery.", "interests": ["device identity", "hardware", "offline resilience"], "availability": "unavailable", "consent": consent(False, False, False, False, True)},
        {"id": "mina-vale", "displayName": "Mina Vale", "role": "developer", "companyId": "lanternmoss-proofworks", "biography": "A fictional developer building understandable selective-disclosure workflows and practical proof tooling.", "interests": ["zero-knowledge proofs", "developer tooling", "selective privacy"], "availability": "open-to-meet", "presenceSlot": "privacy", "consent": consent()},
        {"id": "tariq-fern", "displayName": "Tariq Fern", "role": "developer", "companyId": "copperkite-wallet-studio", "biography": "A fictional front-end developer exploring keyboard-friendly wallets and clear account recovery experiences.", "interests": ["wallets", "accessibility", "account recovery"], "availability": "busy", "presenceSlot": "mingle", "consent": consent()},
        {"id": "inez-brook", "displayName": "Inez Brook", "role": "developer", "companyId": "prismsprout-infrastructure", "biography": "A fictional embedded-systems developer studying receiver diagnostics and honest location uncertainty.", "interests": ["device identity", "hardware", "offline resilience"], "availability": "unknown", "consent": consent(True, True, False, False)},
        {"id": "leah-wren", "displayName": "Leah Wren", "role": "founder", "companyId": "lanternmoss-proofworks", "biography": "A fictional founder looking for practical privacy use cases and carefully scoped pilot partners.", "interests": ["selective privacy", "enterprise adoption", "pilot partnerships"], "availability": "busy", "presenceSlot": "privacy", "consent": consent()},
        {"id": "omar-finch", "displayName": "Omar Finch", "role": "founder", "companyId": "copperkite-wallet-studio", "biography": "A fictional founder meeting designers and community organizers who make wallets easier to understand.", "interests": ["wallets", "accessibility", "professional networking"], "availability": "open-to-meet", "presenceSlot": "mingle", "consent": consent()},
        {"id": "nia-calder", "displayName": "Nia Calder", "role": "founder", "companyId": "prismsprout-infrastructure", "biography": "A fictional founder exploring equipment provenance and reliable convention infrastructure.", "interests": ["asset provenance", "device identity", "offline resilience"], "availability": "open-to-meet", "presenceSlot": "future", "consent": consent()},
        {"id": "suri-moss", "displayName": "Suri Moss", "role": "worker", "companyId": "lanternmoss-proofworks", "biography": "A fictional booth guide who offers short introductory demonstrations when the kiosk queue is quiet.", "interests": ["zero-knowledge proofs", "developer tooling", "introductions"], "availability": "open-to-meet", "presenceSlot": "privacy", "consent": consent()},
        {"id": "theo-birch", "displayName": "Theo Birch", "role": "worker", "companyId": "prismsprout-infrastructure", "biography": "A fictional equipment technician currently servicing a demo receiver and unavailable for meetings.", "interests": ["hardware", "device identity", "offline resilience"], "availability": "busy", "presenceSlot": "future", "consent": consent(True, False, True, True)},
        {"id": "mara-sol", "displayName": "Mara Sol", "role": "worker", "companyId": "sunnyorchard-kitchen", "biography": "A fictional food-service host who helps attendees find dietary options during scheduled breaks.", "interests": ["food", "coffee", "dietary accessibility"], "availability": "open-to-meet", "presenceSlot": "food", "consent": consent(True, False, True, True)},
    ]
    for person in people:
        person["dossierSlug"] = "convention-" + person["id"]
        person["venueIds"] = list(VENUE_IDS)

    kiosks = [
        {"id": "privacy-kiosk", "name": "LanternMoss Privacy Lab", "companyId": "lanternmoss-proofworks", "kind": "crypto", "destinationSlot": "privacy", "workerIds": ["suri-moss", "mina-vale"], "description": "Fictional privacy demonstrations and developer conversations."},
        {"id": "mingle-kiosk", "name": "CopperKite Connection Corner", "companyId": "copperkite-wallet-studio", "kind": "crypto", "destinationSlot": "mingle", "workerIds": ["omar-finch", "tariq-fern"], "description": "Fictional wallet onboarding and participant-controlled networking demonstrations."},
        {"id": "future-kiosk", "name": "PrismSprout Device Workshop", "companyId": "prismsprout-infrastructure", "kind": "crypto", "destinationSlot": "future", "workerIds": ["theo-birch", "nia-calder"], "description": "Fictional equipment provenance, receiver diagnostics, and offline-resilience demonstrations."},
        {"id": "food-kiosk", "name": "SunnyOrchard Coffee and Bowls", "companyId": "sunnyorchard-kitchen", "kind": "food", "destinationSlot": "food", "workerIds": ["mara-sol"], "description": "Fictional coffee, fruit bowls, and dietary-option guidance."},
    ]
    for kiosk in kiosks:
        kiosk["dossierSlug"] = "convention-" + kiosk["id"]
        kiosk["venueIds"] = list(VENUE_IDS)

    device_twins = []
    for number in range(1, 7):
        device_twins.append({
            "id": f"bc021-twin-{number:03d}", "dossierSlug": f"convention-bc021-twin-{number:03d}",
            "name": f"Fictional BC021 tag {number:03d}", "kind": "bc021-tag", "model": "BlueCharm BC021",
            "role": "mobile-tag" if number <= 3 else "kiosk-tag", "venueIds": list(VENUE_IDS),
            "inventoryIdentifier": f"TT-CONV-BC021-{number:03d}", "evidence": "MOCK",
            "capabilities": {"advertises": True, "scansTags": False, "measuresDistance": False, "suppliesTrustedLocation": False, "votesInConsensus": False},
        })
    for number in range(1, 4):
        device_twins.append({
            "id": f"arduino-twin-{number:03d}", "dossierSlug": f"convention-arduino-twin-{number:03d}",
            "name": f"Fictional Arduino receiver {number:03d}", "kind": "arduino-uno-r4", "model": "Arduino UNO R4 WiFi",
            "role": "receiver", "venueIds": list(VENUE_IDS), "inventoryIdentifier": f"TT-CONV-ARDUINO-{number:03d}", "evidence": "MOCK",
            "capabilities": {"advertises": True, "scansTags": True, "measuresDistance": False, "suppliesTrustedLocation": False, "votesInConsensus": False},
            "measurementFreshness": "unknown", "measurementTimestampMs": None,
        })

    assignments = [
        {"id": "assignment-attendee-001", "eventId": EVENT_ID, "deviceId": "bc021-twin-001", "profileId": "avery-bloom", "kind": "temporary-custody", "evidence": "MOCK"},
        {"id": "assignment-developer-001", "eventId": EVENT_ID, "deviceId": "bc021-twin-002", "profileId": "mina-vale", "kind": "temporary-custody", "evidence": "MOCK"},
        {"id": "assignment-founder-001", "eventId": EVENT_ID, "deviceId": "bc021-twin-003", "profileId": "nia-calder", "kind": "temporary-custody", "evidence": "MOCK"},
        {"id": "assignment-privacy-kiosk", "eventId": EVENT_ID, "deviceId": "bc021-twin-004", "kioskId": "privacy-kiosk", "kind": "temporary-placement", "evidence": "MOCK"},
        {"id": "assignment-mingle-kiosk", "eventId": EVENT_ID, "deviceId": "bc021-twin-005", "kioskId": "mingle-kiosk", "kind": "temporary-placement", "evidence": "MOCK"},
        {"id": "assignment-future-kiosk", "eventId": EVENT_ID, "deviceId": "bc021-twin-006", "kioskId": "future-kiosk", "kind": "temporary-placement", "evidence": "MOCK"},
    ]

    return {
        "schema": "testtown/eventrevolution-convention/v1", "datasetId": DATASET_ID,
        "eventId": EVENT_ID, "evidence": "MOCK", "fictional": True,
        "note": "All records are invented rehearsal fixtures. Venue layouts are alternatives, not simultaneous live locations. No real people, companies, label codes, hardware serials, or radio observations are represented.",
        "venues": venues, "people": people, "organizations": organizations,
        "kiosks": kiosks, "deviceTwins": device_twins, "assignments": assignments,
    }


def build_files():
    projection = convention_data()
    files = {PROJECTION_PATH: encoded_json(projection)}
    participation = {
        "schema": "testtown/convention-participation/v1", "eventId": EVENT_ID,
        "evidence": "MOCK", "fictional": True,
        "scope": "Fictional convention participation only. This registry does not establish legal incorporation, government registration, trusted issuer admission, ownership proof, or live device possession.",
        "organizations": {record["dossierSlug"]: {"displayName": record["name"], "status": "participating"} for record in projection["organizations"]},
        "citizens": {record["dossierSlug"]: {"displayName": record["displayName"], "status": "participating"} for record in projection["people"]},
        "assets": {},
    }

    def dossier(category, slug, display_name, extension, story, villain=None):
        directory = f"dossiers/{category}/{slug}"
        document_name = "fictional-evidence.md"
        document = f"# Fictional convention evidence: {display_name}\n\nEvidence: MOCK. This record is invented for {EVENT_ID}; it does not document a real person, business, venue, or device.\n\n{story}\n\nThe mock authority of record is {REGISTRY_PATH}. Its scope is convention participation and synthetic inventory, not government or legal title authority.\n"
        files[f"{directory}/{document_name}"] = document
        record = {
            "schema": "testtown/dossier/v0.1", "category": category[:-1] if category != "assets" else "asset",
            "slug": slug, "displayName": display_name,
            "honesty": {"role": "VILLAIN" if villain else "AUTHENTIC", "fraudMechanism": villain},
            "evidence": "MOCK", "fictional": True,
            "documents": [{"file": document_name, "kind": "fictional-convention-evidence", "sha256": hashlib.sha256(document.encode()).hexdigest(), "confirmableBy": REGISTRY_PATH}],
            **extension,
        }
        files[f"{directory}/dossier.json"] = encoded_json(record)
        return record

    company_slugs = {company["id"]: company["dossierSlug"] for company in projection["organizations"]}
    for company in projection["organizations"]:
        dossier("organizations", company["dossierSlug"], company["name"], {
            "identifiers": {"conventionRegistration": "TT-CONV-ORG-" + company["id"]},
            "participation": {"eventId": EVENT_ID, "kind": company["kind"], "issuerAdmission": "not-requested", "trustedIssuer": False},
            "operator": {"note": "No live wallet, keys, issuer privileges, or legal registration are claimed."},
        }, company["description"])

    for person in projection["people"]:
        dossier("citizens", person["dossierSlug"], person["displayName"], {
            "identifiers": {"conventionParticipantId": "TT-CONV-PERSON-" + person["id"]},
            "employment": ([{"employerSlug": company_slugs[person["companyId"]], "role": person["role"], "from": None, "to": None}] if person.get("companyId") else []),
            "householdSlugs": [],
            "conventionProfile": {key: value for key, value in person.items() if key not in {"dossierSlug", "displayName"}},
            "operator": {"note": "Fictional person. No real personal data, account, or keys are assigned."},
        }, person["biography"])

    asset_records = []
    for venue in projection["venues"]:
        asset_records.append(("convention-venue-" + venue["id"], venue["name"], "real-estate", "TT-CONV-VENUE-" + venue["id"], venue["description"], {
            "venueId": venue["id"], "ownerCitizenSlug": "convention-leah-wren",
            "lifecycle": {"stage": "active", "story": "Fictional venue available as an alternate rehearsal layout.", "kernelExpectations": ["venue identity is separate from the consumer's coordinate geometry"]},
        }))
    for kiosk in projection["kiosks"]:
        asset_records.append((kiosk["dossierSlug"], kiosk["name"], "equipment", "TT-CONV-KIOSK-" + kiosk["id"], kiosk["description"], {
            "ownerOrganizationSlug": company_slugs[kiosk["companyId"]], "venueIds": kiosk["venueIds"],
            "lifecycle": {"stage": "active", "story": "Fictional kiosk equipment rehearsed at a named destination slot.", "kernelExpectations": ["staff profiles remain citizens rather than owned equipment"]},
        }))
    for device in projection["deviceTwins"]:
        asset_records.append((device["dossierSlug"], device["name"], "equipment", device["inventoryIdentifier"], "Synthetic inventory twin only. The identifier is invented and is not copied from a purchased device or a label code.", {
            "ownerOrganizationSlug": "convention-prismsprout-infrastructure", "device": device,
            "lifecycle": {"stage": "active", "story": "Fictional convention equipment with separate event-scoped custody assignments.", "kernelExpectations": ["a copied label does not prove physical possession or ownership", "asset registration does not authorize tracking or consensus voting", "temporary assignment does not transfer permanent ownership"]},
        }))
    for slug, display_name, kind, anchor, story, extension in asset_records:
        record = dossier("assets", slug, display_name, {"assetKind": kind, "identityAnchor": {"kind": "synthetic-inventory-identifier", "value": anchor}, "papers": ["fictional-evidence.md"], **extension}, story)
        participation["assets"][slug] = {"displayName": display_name, "identityAnchor": record["identityAnchor"], "status": "active"}

    villain_slug = "VILLAIN--convention-tag-twin--copied-label-and-cloned-advertisement"
    dossier("assets", villain_slug, "Counterfeit convention tag claiming an existing twin identity", {
        "assetKind": "equipment", "identityAnchor": {"kind": "synthetic-inventory-identifier", "value": "TT-CONV-BC021-001"},
        "claimedOwnership": "An unregistered operator presents a copied label and duplicated advertisement.",
        "papers": ["fictional-evidence.md"],
        "lifecycle": {"stage": "fraud-cloned-anchor", "story": "A readable copied code cannot prove which physical device is genuine.", "kernelExpectations": ["the duplicate identity binding is detected and held for review", "first registration alone does not prove legitimate ownership", "the clone cannot become a fresh location observation or a consensus voter"]},
    }, "This deliberately fraudulent twin copies the registered synthetic identifier. The authority registry contains only the authentic asset.", "copied synthetic label and radio advertisement do not establish possession or authorized ownership")

    stale_slug = "VILLAIN--convention-receiver--retained-signal-presented-as-fresh-proof"
    dossier("assets", stale_slug, "Convention receiver presenting retained signal as fresh location proof", {
        "assetKind": "equipment", "identityAnchor": {"kind": "synthetic-inventory-identifier", "value": "TT-CONV-RETAINED-READING-001"},
        "claimedOwnership": "An untrusted operator claims the board can authorize a person's location.",
        "papers": ["fictional-evidence.md"],
        "lifecycle": {"stage": "fraud-stale-measurement", "story": "Legacy board elapsed time is passed off as the epoch time of an individual retained measurement.", "kernelExpectations": ["measurement freshness stays unknown when individual timestamps are absent", "the diagnostic cannot become a position fix or consensus vote", "radio address counts cannot become attendee counts"]},
    }, "The malicious claim concerns measurement interpretation, not a verified physical attack. It is a fictional failure-mode fixture.", "retained signal and board uptime are misrepresented as fresh authenticated person-location evidence")

    files[REGISTRY_PATH] = encoded_json(participation)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify deterministic bytes without writing files")
    args = parser.parse_args()
    expected_files = build_files()
    failures = []
    for relative, content in expected_files.items():
        path = ROOT / relative
        if path.exists():
            if path.read_bytes() != content.encode("utf-8"):
                failures.append(f"existing content differs: {relative}")
        elif args.check:
            failures.append(f"missing: {relative}")
    if failures:
        raise SystemExit("Refusing to overwrite existing content:\n" + "\n".join(failures))
    if not args.check:
        for relative, content in expected_files.items():
            path = ROOT / relative
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(content)
    print(f"{'verified' if args.check else 'created or verified'} {len(expected_files)} deterministic fixture files")


if __name__ == "__main__":
    main()
