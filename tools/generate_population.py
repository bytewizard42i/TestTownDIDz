#!/usr/bin/env python3
"""
generate_population.py — TestTown's single source of truth.

Regenerates the registries (mock IRS + State corporations) AND every
organization/citizen/animal/asset dossier from the POPULATION tables below,
so the dossiers and the authorities of record can never drift apart.

Idempotent: run it any time; it rewrites generated files in place.
Hand-written document files (articles-of-incorporation.md etc.) are
preserved and re-hashed; orgs without one get a generated charter-note.md.

Run:  python3 tools/generate_population.py
"""

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Operator wallets (PUBLIC addresses only — seeds live in the local vault).
LADIES = {
    "sarah":   "mn_addr_preprod17jsz4gpr2t3qsw3nmw2hert4tc0ltu84d86lnc45rjgv4cp8muwsxplsm2",
    "jessica": "mn_addr_preprod19r90qtcekt224vgmmhd4q4625w7kn3epgw32k09wguy0tnsqrlnqh28dn9",
    "monica":  "mn_addr_preprod1v4mjk8pf9hkxwkc3d6nd53c2v4m2gmvesrusghpgaucma9glc4vs6fw4a9",
    "rachel":  "mn_addr_preprod1mr9rndczh2zxcu0mlfhem63x4ledl88kvl4xl2jv3j5mfgrm7gasmqqfvc",
    "emma":    "mn_addr_preprod15yyy5az5crv2f8usjxg5hurwyyknv8g93648f4n68450yd5c555stt4wdt",
    "olivia":  "mn_addr_preprod1mw7e5j8r0nv3gr3cc9zfyz78wsygfy5e2zku4933jpchg7mam85s7rvvjc",
    "nadia":   "mn_addr_preprod12htexfpvc870xzz5lx50jv33vj5kfuls3efatn724hfet3uldt7sud377s",
    "tessa":   "mn_addr_preprod1xnqxhtmnklw6wxujzky5gaap0q8hatxlmppwhfwfczrdvgfdeqpscnw6f4",
    "bianca":  "mn_addr_preprod13w30su4w5tmam849gs7r8n8ymv729ymjpjw26dzgch8nmgkytgzsmanal2",
    "greta":   "mn_addr_preprod1t59xn4jmdht9k5utzk5puu9ydqsc4p4y8rzg65fjn23wq0ys9xrsm8tdyh",
}

def org(slug, name, ein, reg, founded, issuer_type, assurance, scopes, tiers,
        officers, operator=None, standing="GOOD_STANDING", ein_status="active",
        villain=None, extra_authority=None, kind=None):
    return dict(slug=slug, name=name, ein=ein, reg=reg, founded=founded,
                issuer_type=issuer_type, assurance=assurance, scopes=scopes,
                tiers=tiers, officers=officers, operator=operator,
                standing=standing, ein_status=ein_status, villain=villain,
                extra_authority=extra_authority or {}, kind=kind)

# ---------------------------------------------------------------------------
# THE CIVIC INSTITUTIONS (featured issuers, operated by the named ladies)
# ---------------------------------------------------------------------------
ORGS = [
    org("st-brigids-general-hospital", "St. Brigid's General Hospital",
        "82-4410973", "PA-C-0048291", "1987-04-12", "hospital", "REGULATED_ENTITY",
        ["BIRTH_CERTIFICATE", "MEDICAL_RECORD"], ["human"],
        [("Maren Okafor", "Administrator"), ("Luis Reyes", "CFO")], "sarah"),
    org("maple-hollow-elementary-school", "Maple Hollow Elementary School",
        "31-7702158", "PA-G-0000031", "1962-08-01", "school-k12", "PEER_REVIEWED",
        ["EDUCATION_K12"], ["human"], [("Dana Whitfield", "Principal")], "greta",
        kind="government-agency"),
    org("maple-hollow-middle-school", "Maple Hollow Middle School",
        "31-7702159", "PA-G-0000032", "1962-08-01", "school-k12", "PEER_REVIEWED",
        ["EDUCATION_K12"], ["human"], [("Ibrahim Diallo", "Principal")], "greta",
        kind="government-agency"),
    org("maple-hollow-senior-high-school", "Maple Hollow Senior High School",
        "31-7702160", "PA-G-0000033", "1962-08-01", "school-k12", "PEER_REVIEWED",
        ["EDUCATION_K12", "DIPLOMA"], ["human"], [("Carol Nakamura", "Principal")], "greta",
        kind="government-agency"),
    org("keystone-ridge-college", "Keystone Ridge College",
        "23-5561201", "PA-C-0011203", "1911-09-01", "college", "REGULATED_ENTITY",
        ["DEGREE", "ENROLLMENT"], ["human"],
        [("Priya Natarajan", "President")], "rachel",
        extra_authority={"accreditor": "Mid-Atlantic Commission on Higher Education"}),
    org("commonwealth-dmv-testtown-office", "Commonwealth Department of Motor Vehicles, TestTown Office",
        "45-0093377", "PA-G-0000017", "1971-01-04", "dmv", "SYSTEM_CRITICAL",
        ["DRIVERS_LICENSE", "VEHICLE_TITLE"], ["human", "rwa"],
        [("Gwen Harper", "Office Director")], "jessica", kind="government-agency"),
    org("testtown-social-security-field-office", "TestTown Social Security Field Office",
        "52-8814406", "PA-G-0000004", "1954-06-30", "ssa", "SYSTEM_CRITICAL",
        ["SSN_BINDING"], ["human"],
        [("Ellis Vance", "Field Office Manager")], "monica", kind="government-agency"),
    org("willow-creek-veterinary-clinic", "Willow Creek Veterinary Clinic",
        "88-2245910", "PA-C-0290114", "2003-03-01", "veterinary", "REGULATED_ENTITY",
        ["VACCINATION", "MICROCHIP_BINDING"], ["animal"],
        [("Dr. Sam Whittaker", "DVM, Owner")], "olivia"),
    org("testtown-animal-hospital-and-equine-center", "TestTown Animal Hospital & Equine Center",
        "88-2245911", "PA-C-0187330", "1998-09-20", "veterinary", "REGULATED_ENTITY",
        ["VACCINATION", "MICROCHIP_BINDING", "HEALTH_CERT", "LINEAGE"], ["animal"],
        [("Dr. Amara Chen", "DVM, Chief of Medicine")], "emma"),
    org("torque-and-timing-auto-works", "Torque & Timing Auto Works",
        "61-3308825", "PA-C-0356102", "2010-05-10", "mechanic", "PEER_REVIEWED",
        ["INSPECTION", "SERVICE_RECORD"], ["rwa"],
        [("Ray Okonkwo", "Owner/Master Technician")], "tessa"),
    org("hearthstone-realty-group", "Hearthstone Realty Group",
        "74-6650391", "PA-C-0244875", "1995-02-01", "real-estate", "REGULATED_ENTITY",
        ["DEED", "APPRAISAL"], ["rwa"],
        [("Vivian Cross", "Managing Broker")], "nadia"),
    org("meridian-horological-appraisals", "Meridian Horological Appraisals LLC",
        "39-1120458", "PA-C-0433981", "2015-11-15", "appraiser", "PEER_REVIEWED",
        ["AUTHENTICITY", "APPRAISAL"], ["rwa"],
        [("Jules Fontaine", "Certified Appraiser")], "bianca"),
]

# ---------------------------------------------------------------------------
# THE VILLAINS (verbose, intuitive labels; frauds live in the DETAILS)
# ---------------------------------------------------------------------------
VILLAINS = [
    org("VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry",
        "Shady Docs LLC (dba TestTown Credential Services)",
        "94-7316285", "PA-C-9990001", "2024-01-05", "appraiser", "SYSTEM_CRITICAL",
        ["BIRTH_CERTIFICATE", "DRIVERS_LICENSE", "DEGREE", "APPRAISAL"],
        ["human", "agent", "animal", "rwa"], [("P. Fictus", "Managing Member")],
        villain="EIN 94-7316285 is well-formed but was NEVER issued by the IRS "
                "registry, and claimed state filing PA-C-9990001 does not exist "
                "in the State corporations registry. Bonus tell: grossly "
                "over-broad scope request at maximum assurance."),
    org("VILLAIN--first-dmv-of-delaware--impersonates-dissolved-entity",
        "First DMV of Delaware Inc.",
        "77-4491062", "DE-C-0092716", "1988-06-20", "dmv", "SYSTEM_CRITICAL",
        ["DRIVERS_LICENSE", "VEHICLE_TITLE"], ["human", "rwa"],
        [("M. Hollowell", "Director (claimed)")],
        villain="Real historical identifiers, dead entity: the IRS registry "
                "shows EIN 77-4491062 REVOKED and the State registry shows "
                "DE-C-0092716 DISSOLVED (2009-03-31); claimed officers do not "
                "match the historical record. A zombie wearing a real name."),
    org("VILLAIN--evergreen-diploma-mill--accreditation-cites-nonexistent-board",
        "Evergreen Institute of Advanced Studies",
        "33-8080441", "PA-C-0512236", "2019-06-14", "college", "REGULATED_ENTITY",
        ["DEGREE", "ENROLLMENT"], ["human"],
        [("Dr. R. Verdant", "Provost")],
        villain="Identity papers are GENUINE (EIN active, registration in good "
                "standing) — the fraud is in the AUTHORITY layer: its claimed "
                "accreditor, the 'National Board of Continental Academics', "
                "does not exist in any registry. The gate must check authority "
                "papers, not just identity papers.",
        extra_authority={"accreditor": "National Board of Continental Academics"}),
]

# ---------------------------------------------------------------------------
# THE EMPLOYERS (twenty jobs; PEER_REVIEWED; EMPLOYMENT/INCOME_RANGE scopes)
# ---------------------------------------------------------------------------
EMPLOYER_NAMES = [
    "Susquehanna Steelworks", "Ironclad Insurance Group", "TestTown Savings & Loan",
    "Blue Heron Bakery", "Copper Kettle Diner", "Nightowl Data Systems",
    "Maple & Main Bookshop", "TestTown Transit Authority", "Green Gable Landscaping",
    "Harvest Moon Grocers", "Riverbend Construction Co.", "Starlight Cinema",
    "Petal & Stem Florists", "TestTown Courier Collective", "Anvil & Oak Furniture Makers",
    "Clearwater Plumbing & Heating", "Foxglove Pharmacy", "Summit Peak Outfitters",
    "Gilded Frame Art Gallery", "Quarry Road Trucking",
]

def slugify(name):
    out = name.lower()
    for ch in "&.,'": out = out.replace(ch, "")
    return "-".join(out.split())

EMPLOYERS = []
for i, name in enumerate(EMPLOYER_NAMES):
    EMPLOYERS.append(org(
        slugify(name), name,
        f"20-40{i:05d}"[:2] + "-" + f"40{i:05d}",  # deterministic fake EIN 20-40000NN
        f"PA-C-06{i:05d}", f"{1958 + (i * 3) % 60}-0{(i % 9) + 1}-15",
        "employer", "PEER_REVIEWED", ["EMPLOYMENT", "INCOME_RANGE"], ["human"],
        [(f"Officer {i + 1}", "Registered Agent")]))

# ---------------------------------------------------------------------------
# THE CITIZENS (twenty residents; jobs point at real org slugs)
# ---------------------------------------------------------------------------
CITIZENS = [
    ("rosa-delgado", "Rosa Delgado", "1989-03-17", "torque-and-timing-auto-works", "Service Manager"),
    ("amos-fairweather", "Amos Fairweather", "1978-11-02", "susquehanna-steelworks", "Foreman"),
    ("june-okafor", "June Okafor", "1994-06-21", "st-brigids-general-hospital", "Registered Nurse"),
    ("theo-brandt", "Theo Brandt", "1985-01-30", "ironclad-insurance-group", "Claims Adjuster"),
    ("mei-lin-zhao", "Mei-Lin Zhao", "1991-09-12", "nightowl-data-systems", "Systems Engineer"),
    ("harold-quist", "Harold Quist", "1957-05-05", "maple-main-bookshop", "Owner-Clerk"),
    ("priscilla-vance", "Priscilla Vance", "1983-02-14", "testtown-savings-loan", "Branch Manager"),
    ("diego-marchetti", "Diego Marchetti", "1996-07-08", "blue-heron-bakery", "Head Baker"),
    ("keisha-lawton", "Keisha Lawton", "1990-12-01", "testtown-transit-authority", "Dispatcher"),
    ("olaf-bjornsen", "Olaf Bjornsen", "1972-04-19", "riverbend-construction-co", "Site Supervisor"),
    ("fern-whitaker", "Fern Whitaker", "1999-08-27", "petal-stem-florists", "Floral Designer"),
    ("marcus-reid", "Marcus Reid", "1988-10-03", "quarry-road-trucking", "Long-Haul Driver"),
    ("anya-petrova", "Anya Petrova", "1993-03-25", "foxglove-pharmacy", "Pharmacist"),
    ("colin-mcbride", "Colin McBride", "1980-06-30", "clearwater-plumbing-heating", "Master Plumber"),
    ("sadie-blackfeather", "Sadie Blackfeather", "1995-11-11", "gilded-frame-art-gallery", "Curator"),
    ("victor-osei", "Victor Osei", "1986-09-09", "harvest-moon-grocers", "Store Manager"),
    ("lena-hartmann", "Lena Hartmann", "1992-01-22", "starlight-cinema", "Projectionist"),
    ("raj-patel", "Raj Patel", "1975-07-16", "summit-peak-outfitters", "Owner"),
    ("bonnie-lachance", "Bonnie LaChance", "1998-04-04", "copper-kettle-diner", "Line Cook"),
    ("edgar-morrow", "Edgar Morrow", "1969-12-24", "anvil-oak-furniture-makers", "Master Joiner"),
]

# slug, name, species, chip, custodian, vet
ANIMALS = [
    ("comet-the-thoroughbred", "Comet (Thoroughbred gelding, b. 2019)", "horse",
     "985-141-002-776-31", "rosa-delgado", "testtown-animal-hospital-and-equine-center"),
    ("biscuit-the-corgi", "Biscuit (Pembroke Welsh Corgi, b. 2022)", "dog",
     "985-141-002-119-04", "june-okafor", "willow-creek-veterinary-clinic"),
    ("smokey-the-barn-cat", "Smokey (domestic shorthair, b. 2020)", "cat",
     "985-141-002-450-77", "harold-quist", "willow-creek-veterinary-clinic"),
    ("duchess-the-warmblood", "Duchess (Hanoverian mare, b. 2017)", "horse",
     "985-141-002-333-58", "raj-patel", "testtown-animal-hospital-and-equine-center"),
]

# slug, name, kind, anchor-kind, anchor, owner
ASSETS = [
    ("heirloom-lange-1815-wristwatch", "A. Lange-style 1815 heirloom wristwatch (fictional)",
     "watch", "serial-number", "TT-1815-004417", "rosa-delgado"),
    ("morrow-family-farmhouse", "Morrow family farmhouse, 44 Quarry Road",
     "real-estate", "parcel-id", "TT-PARCEL-0917-114", "edgar-morrow"),
    ("fairweather-pickup-truck", "Fairweather 2018 pickup truck",
     "vehicle", "vin", "1TTFW18X7JZ004821", "amos-fairweather"),
    ("zhao-grand-seiko-snowflake", "Zhao Grand Seiko-style 'Snowflake' wristwatch (fictional)",
     "watch", "serial-number", "TT-GS-2210-88031", "mei-lin-zhao"),
]

# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def ensure_charter(org_dir, o):
    """Preserve hand-written articles; otherwise generate a charter note."""
    articles = os.path.join(org_dir, "articles-of-incorporation.md")
    if os.path.exists(articles):
        return "articles-of-incorporation.md", sha256_file(articles)
    charter = os.path.join(org_dir, "charter-note.md")
    os.makedirs(org_dir, exist_ok=True)
    with open(charter, "w") as f:
        f.write(f"# Charter note — {o['name']}\n\n"
                f"State filing {o['reg']} · founded {o['founded']} · EIN {o['ein']}\n\n"
                f"Purpose: operations as a {o['issuer_type']} in TestTown.\n\n"
                f"*(TestTown fixture document; its sha256 is the dossier's commitment.)*\n")
    return "charter-note.md", sha256_file(charter)

def org_dossier(o):
    d = os.path.join(ROOT, "dossiers", "organizations", o["slug"])
    doc, digest = ensure_charter(d, o)
    lady = o.get("operator")
    write_json(os.path.join(d, "dossier.json"), {
        "schema": "testtown/dossier/v0.1",
        "category": "organization",
        "slug": o["slug"],
        "displayName": o["name"],
        "honesty": {"role": "VILLAIN" if o["villain"] else "AUTHENTIC",
                     "fraudMechanism": o["villain"]},
        "identifiers": {"ein": o["ein"], "stateRegistration": o["reg"], "founded": o["founded"]},
        "authority": {"issuerType": o["issuer_type"],
                       "requestedAssuranceLevel": o["assurance"],
                       "attestationScopes": o["scopes"],
                       "subjectTiers": o["tiers"],
                       **o["extra_authority"]},
        "officers": [{"name": n, "role": r} for n, r in o["officers"]],
        "documents": [{"file": doc, "kind": "incorporation-record", "sha256": digest,
                        "confirmableBy": "registries/state-corporations-registry.json"}],
        "operator": ({"walletCard": f"utils_Midnight/preProd-Wallets/wallets/wallet-{lady}.md",
                       "preprodAddress": LADIES[lady]} if lady
                      else {"walletCard": None, "preprodAddress": None,
                            "note": "bulk org — headless derived key planned"}),
    })

def main():
    all_orgs = ORGS + EMPLOYERS + VILLAINS

    # --- registries (the authorities of record) ---
    eins, regs = {}, {}
    for o in ORGS + EMPLOYERS:
        eins[o["ein"]] = {"legalName": o["name"], "issued": o["founded"], "status": o["ein_status"]}
        regs[o["reg"]] = {"legalName": o["name"], "standing": o["standing"],
                           "incorporated": o["founded"],
                           "officers": [f"{n} ({r})" for n, r in o["officers"]],
                           **({"kind": o["kind"]} if o["kind"] else {})}
    # zombie villain: REAL identifiers, dead status (the tell is the status)
    zombie = VILLAINS[1]
    eins[zombie["ein"]] = {"legalName": zombie["name"], "issued": "1988-07-07",
                            "status": "revoked",
                            "revokedReason": "entity dissolved 2009-03-31; EIN retired"}
    regs[zombie["reg"]] = {"legalName": zombie["name"], "standing": "DISSOLVED",
                            "incorporated": zombie["founded"], "dissolved": "2009-03-31",
                            "officers": ["T. Ashworth (Director, historical)"],
                            "note": "VILLAIN tell: villain dossier claims good standing and "
                                    "different officers"}
    # diploma mill: genuine identity papers (fraud is in the authority layer)
    mill = VILLAINS[2]
    eins[mill["ein"]] = {"legalName": mill["name"], "issued": mill["founded"], "status": "active"}
    regs[mill["reg"]] = {"legalName": mill["name"], "standing": "GOOD_STANDING",
                          "incorporated": mill["founded"],
                          "officers": ["Dr. R. Verdant (Provost)"]}

    write_json(os.path.join(ROOT, "registries", "irs-ein-registry.json"), {
        "registry": "TestTown mock IRS — Employer Identification Number registry",
        "note": "The authority of record for EINs. If an EIN is not in here, the IRS "
                "never issued it — no matter how well-formed it looks. GENERATED by "
                "tools/generate_population.py; edit the tables there, not this file.",
        "eins": eins,
        "deliberately_absent": {
            "94-7316285": "claimed by VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry "
                           "(well-formed, never issued)"},
    })
    write_json(os.path.join(ROOT, "registries", "state-corporations-registry.json"), {
        "registry": "TestTown mock State Corporations registry (Secretary of State)",
        "note": "The authority of record for legal existence and standing. GENERATED by "
                "tools/generate_population.py; edit the tables there, not this file.",
        "accreditors_of_record": ["Mid-Atlantic Commission on Higher Education"],
        "registrations": regs,
        "deliberately_absent": {
            "PA-C-9990001": "claimed by VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry",
            "National Board of Continental Academics":
                "cited by VILLAIN--evergreen-diploma-mill--accreditation-cites-nonexistent-board; "
                "no such accreditor exists in any registry"},
    })

    # --- dossiers ---
    for o in all_orgs:
        org_dossier(o)

    citizens_with_household = {c[0]: {"animals": [], "assets": []} for c in CITIZENS}
    for a in ANIMALS: citizens_with_household[a[4]]["animals"].append(a[0])
    for a in ASSETS:  citizens_with_household[a[5]]["assets"].append(a[0])

    for slug, name, born, employer, role in CITIZENS:
        write_json(os.path.join(ROOT, "dossiers", "citizens", slug, "dossier.json"), {
            "schema": "testtown/dossier/v0.1", "category": "citizen", "slug": slug,
            "displayName": name,
            "honesty": {"role": "AUTHENTIC", "fraudMechanism": None},
            "identifiers": {"born": born, "birthRecordIssuer": "st-brigids-general-hospital"},
            "employment": [{"employerSlug": employer, "role": role,
                             "from": f"{max(int(born[:4]) + 18, 2005)}-06-01", "to": None}],
            "householdSlugs": citizens_with_household[slug],
            "documents": [],
            "operator": {"note": "Citizens hold their OWN keys — self-sovereign; "
                                  "wallet assignment lands with the admission-gate build."},
        })

    for slug, name, species, chip, custodian, vet in ANIMALS:
        write_json(os.path.join(ROOT, "dossiers", "animals", slug, "dossier.json"), {
            "schema": "testtown/dossier/v0.1", "category": "animal", "slug": slug,
            "displayName": name,
            "honesty": {"role": "AUTHENTIC", "fraudMechanism": None},
            "species": species,
            "identityBinding": {"kind": "microchip", "chipId": chip, "implantedBy": vet},
            "custodianCitizenSlug": custodian, "careHistory": [], "documents": [],
        })

    for slug, name, kind, anchor_kind, anchor, owner in ASSETS:
        write_json(os.path.join(ROOT, "dossiers", "assets", slug, "dossier.json"), {
            "schema": "testtown/dossier/v0.1", "category": "asset", "slug": slug,
            "displayName": name,
            "honesty": {"role": "AUTHENTIC", "fraudMechanism": None},
            "assetKind": kind,
            "identityAnchor": {"kind": anchor_kind, "value": anchor},
            "ownerCitizenSlug": owner, "papers": [], "documents": [],
        })

    print(f"generated: {len(all_orgs)} organizations ({len(VILLAINS)} villains), "
          f"{len(CITIZENS)} citizens, {len(ANIMALS)} animals, {len(ASSETS)} assets")

if __name__ == "__main__":
    main()
