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
    # Wallets 11 to 20, added Nov 26 2026 as SPARES: no institution is
    # assigned to them yet. Every roster name starts with a different letter
    # so two can never be confused at a glance. To put one to work, name it
    # as the operator of an organization in the ORGS table below.
    "adele":   "mn_addr_preprod17q0m3k77jjqt9s8g40slahsc802pswnn0v4zr262n9naetnuss0qn8eq4y",
    "daphne":  "mn_addr_preprod1avegu273cz7qqrzg40tnhdzgvwedl8ndy79pejn3wh2rshpdf4nsgtql58",
    "fiona":   "mn_addr_preprod18xm2q8u4vpkl7txm5tnegtqglfq5y8jlx8vlesuqaj0q0rdj4p4sqt88nn",
    "hazel":   "mn_addr_preprod1l9tug0m92sky9zh5tpr2ct4mux49flva5xqyvdggvfjd2sh8wfysp2asls",
    "iris":    "mn_addr_preprod1e0c6pd2n3uv979lcnwf53qdkr3pp4y7rrrh0ljcdpe4trv5gvryqfqy88m",
    "kira":    "mn_addr_preprod1l5hdl6dqvchzjuylve3kdcwlk897gnf6e8lxwsh8f5m6ql6n7agqgk7nrn",
    "lydia":   "mn_addr_preprod1qkpsc8yvptne82gm3znzjzl2tpe9s8s52lsupl7pne9cgqepjjgqc5rzd2",
    "paloma":  "mn_addr_preprod1jgsxrlqujujhrc3fuqexdmpqqxcmf7a5wc324vmlrzkvqn4cnt0qyw07q2",
    "quinn":   "mn_addr_preprod1yx5kfx87xxlg0xg7qwrrr9uxs4dw9y57e7fspvnwhlq28fxt47ks2rljnm",
    "violet":  "mn_addr_preprod19476j2yd7ul8v7l3urxxyk7j49gd8qcucs5r09nk6ff7cw6nmayq2r8awq",
}

# Headless wallets for everyone else: every resident citizen, every other
# organization (villains included: a villain needs a key to attempt fraud),
# and the exchange's signers. PUBLIC addresses only. The file is written when
# wallets are created; the seeds never enter this repo (docs/SECRETS_CONVENTION.md).
# Convention fixtures are deliberately absent: their own tests forbid a key.
with open(os.path.join(ROOT, "tools", "wallet-assignments.json")) as _f:
    WALLETS = json.load(_f)["wallets"]

def wallet_card(slug):
    return f"utils_Midnight/preProd-Wallets/wallets/wallet-{slug}.md"

def wallet_address(slug):
    return WALLETS[slug]["preprodAddress"]

def org(slug, name, ein, reg, founded, issuer_type, assurance, scopes, tiers,
        officers, operator=None, standing="GOOD_STANDING", ein_status="active",
        villain=None, extra_authority=None, kind=None, extra=None):
    # `extra` = additional top-level blocks for this dossier (e.g. "exchange").
    return dict(slug=slug, name=name, ein=ein, reg=reg, founded=founded,
                issuer_type=issuer_type, assurance=assurance, scopes=scopes,
                tiers=tiers, officers=officers, operator=operator,
                standing=standing, ein_status=ein_status, villain=villain,
                extra_authority=extra_authority or {}, kind=kind, extra=extra or {})

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
# THE EXCHANGE (Nov 25 2026): a business that holds crypto for itself and
# for its customers, in multi-signature wallets.
#
# WHY IT IS HERE
#   Wallet insurance, screening and custody questions all need a custodian in
#   the town: somebody whose wallet is NOT controlled by one key. The exchange
#   gives every consumer the two shapes that matter:
#     1. a CORPORATE wallet the company controls (2 of its 3 officers sign)
#     2. a CUSTOMER wallet the company holds FOR a customer (any 2 of 3:
#        the customer, the exchange, and an independent recovery trustee)
#
# WHAT IS REAL AND WHAT IS A PLACEHOLDER
#   Real: every signer has a pre-prod address derived from a seed in the vault.
#   Placeholder: the multi-sig wallets themselves. Midnight has no native
#   multi-signature account, so each one must be a contract that counts
#   approvals, and that contract is not written or deployed yet. Each wallet
#   dossier carries a `placeholders` list saying exactly what is missing and
#   what would unblock it. Fill those in; do not delete them silently.
#
# WHY issuerType IS "employer"
#   The admission gate admits only issuer types it has a policy for, and a
#   never-delete test says every AUTHENTIC organization must be admitted. An
#   "exchange" issuer type (attesting custody or account standing) is a good
#   idea for later; adding it means adding a gate policy first. Until then the
#   exchange registers as what it also truthfully is: an employer.
#
# IDEAS, NOT BUILT
#   - a VILLAIN exchange: looks solvent, but its treasury signers are one person
#   - proof of reserves: the exchange proves it holds at least what it owes
#   - a customer withdrawing while the exchange refuses to co-sign (the
#     recovery trustee exists for exactly this)
#   - an omnibus wallet holding many customers' funds in one account
#   - the exchange as a KYC issuer for its own customers
# ---------------------------------------------------------------------------
EXCHANGE_SLUG = "quarry-street-exchange"
EXCHANGE_TREASURY_WALLET = "quarry-street-exchange-treasury-wallet"
EXCHANGE_RECOVERY_TRUSTEE = "testtown-savings-loan"
EXCHANGE_OFFICERS = [
    ("Naomi Castellan", "Chief Executive Officer"),
    ("Desmond Achterberg", "Chief Financial Officer"),
    ("Ingrid Solheim", "Chief Compliance Officer"),
]
# customer citizen slug -> the custody wallet the exchange holds for them
EXCHANGE_CUSTOMER_WALLETS = {"mei-lin-zhao": "zhao-exchange-custody-wallet"}

MULTISIG_PLACEHOLDERS = [
    {"field": "identityAnchor.value", "status": "PLACEHOLDER",
     "reason": "No multi-sig account exists yet. Midnight has no native "
               "multi-signature account or account abstraction, so this wallet "
               "must be a Compact contract that counts approvals. That contract "
               "has not been written or deployed.",
     "unblockedBy": "Write and deploy a multi-party authorization contract on "
                    "pre-prod, then record its contract address here."},
    {"field": "holdings.balanceUsd", "status": "PLACEHOLDER",
     "reason": "Nothing is funded. The signer keys are real pre-prod addresses "
               "holding no tNIGHT.",
     "unblockedBy": "Fund the signers from the faucet or a funded wallet."},
    {"field": "custody.assetCustody", "status": "PLACEHOLDER",
     "reason": "Not verified here that a contract on current pre-prod can hold "
               "tNIGHT on behalf of its signers. Midnight's own contract-custody "
               "account design (Midnight Passport, MIP-0012 and MIP-0013) was "
               "at the Proposed stage and Stagenet-only as of 3 Oct 2026.",
     "unblockedBy": "Confirm against the current support matrix, then test with "
                    "a small funded contract."},
]

EXCHANGES = [
    org(EXCHANGE_SLUG, "Quarry Street Exchange",
        "20-4000020", "PA-C-0600020", "2021-09-14",
        "employer", "PEER_REVIEWED", ["EMPLOYMENT", "INCOME_RANGE"], ["human"],
        EXCHANGE_OFFICERS,
        extra={"exchange": {
            "kind": "centralized-exchange",
            "story": "TestTown's first digital-asset exchange, opened on Quarry "
                     "Street in 2021. It keeps its own funds in a treasury that "
                     "needs two of its three officers to move, and it holds each "
                     "customer's funds in a wallet the customer co-controls.",
            "corporateWallets": [EXCHANGE_TREASURY_WALLET],
            "customerWallets": sorted(EXCHANGE_CUSTOMER_WALLETS.values()),
            "customers": sorted(EXCHANGE_CUSTOMER_WALLETS),
            "customerWalletTemplate": {
                "threshold": 2, "signerCount": 3,
                "signerRoles": ["customer", "exchange-cosigner", "recovery-trustee"],
                "recoveryTrusteeOrganizationSlug": EXCHANGE_RECOVERY_TRUSTEE,
                "why": "Any two of the three must approve. No party can move "
                       "funds alone. Customer plus trustee works without the "
                       "exchange, so the customer cannot be locked out. Exchange "
                       "plus trustee works without the customer, which is the "
                       "recovery path if the customer loses their key, and also "
                       "the trust a customer is placing in the two of them.",
            },
            "testWired": {
                "signerKeys": "real pre-prod addresses, unfunded",
                "multiSigAccounts": "PLACEHOLDER (see each wallet dossier)",
            },
        }}),
]

# ---------------------------------------------------------------------------
# THE PRODUCT CATALOG (what the town's shops have on the shelf)
#
# WHY IT EXISTS
#   Citizens already voice WANTS (docs/INTENTS_LAYER.md): "insure this wallet
#   for $500". Until now nobody in town SOLD anything, so a want had nothing
#   to meet. A product is the other half: a shop saying "we sell this, on
#   these terms, to anyone". Read docs/PRODUCT_CATALOG.md for the long version.
#
# A PRODUCT IS NOT AN OFFER AND NOT A POLICY
#   A product is the same for everybody, like a menu. It never names a
#   customer and never says who qualifies. Who was offered what, and who was
#   bound to which terms, are OUTCOMES and belong to the seller's own system.
#
# WHO IS WHO
#   underwriter  carries the risk. Ironclad Insurance Group, the town insurer.
#   sellers      put it on a shelf. Quarry Street Exchange sells wallet cover
#                to the people whose wallets it already knows; Ironclad also
#                sells direct.
#
# THESE NUMBERS ARE PLACEHOLDERS
#   Round, invented, and deliberately not anybody's real pricing. A consumer
#   with real terms keeps them in its own private repo, in this same shape.
#
# IDEAS, NOT BUILT
#   - a licence registry (a State Insurance Department) so "is this
#     underwriter allowed to sell insurance?" has an authority of record
#   - non-insurance products: a loan, a custody plan, a vet wellness plan
#   - cover on a person (health, life) once a fixture needs it
#   - bundles and riders ("wallet cover + hardware wallet discount")
# ---------------------------------------------------------------------------
INSURER_SLUG = "ironclad-insurance-group"

# The generic names of the checks a wallet-cover buyer must clear. These say
# what is ASKED for, never who passed.
WALLET_COVER_CHECKS = ["screening-check", "region-check", "identity-check",
                       "education-check", "wallet-control-check"]

def insurance_product(slug, name, sellers, covers_category, covers_kinds, peril,
                      low, high, deductible, premium, months, requires, story,
                      status="on-sale", listed="2026-10-01", withdrawn=None,
                      underwriter=INSURER_SLUG, villain=None):
    return dict(slug=slug, name=name, sellers=sellers, underwriter=underwriter,
                covers={"dossierCategory": covers_category, "kinds": covers_kinds},
                peril=peril, low=low, high=high, deductible=deductible,
                premium=premium, months=months, requires=requires, story=story,
                status=status, listed=listed, withdrawn=withdrawn, villain=villain)

WALLET_THEFT = "unauthorized transfer out of the insured wallet"

PRODUCTS = [
    # Three sizes of the same wallet cover. The ranges touch but never
    # overlap, so any amount from $100 to $25,000 fits exactly one of them.
    insurance_product(
        "wallet-theft-cover-starter", "Wallet Theft Cover, Starter",
        [EXCHANGE_SLUG, INSURER_SLUG], "asset", ["crypto-wallet"], WALLET_THEFT,
        100, 1000, 50, 20, 12, WALLET_COVER_CHECKS[:3],
        "The small one, for a first wallet. Fewest checks, lowest price."),
    insurance_product(
        "wallet-theft-cover-standard", "Wallet Theft Cover, Standard",
        [EXCHANGE_SLUG, INSURER_SLUG], "asset", ["crypto-wallet"], WALLET_THEFT,
        1001, 5000, 150, 60, 12, WALLET_COVER_CHECKS,
        "The middle one. Asks for every check the town knows how to run."),
    insurance_product(
        "wallet-theft-cover-plus", "Wallet Theft Cover, Plus",
        [EXCHANGE_SLUG, INSURER_SLUG], "asset", ["crypto-wallet"], WALLET_THEFT,
        5001, 25000, 500, 200, 12, WALLET_COVER_CHECKS,
        "The large one, for savings. Same checks as Standard, bigger numbers."),
    # A product that is NOT about wallets, to prove the shape is generic:
    # the same catalog serves a horse. Ember the broodmare is the town's
    # insured-animal lifecycle fixture.
    insurance_product(
        "equine-mortality-cover", "Equine Mortality Cover",
        [INSURER_SLUG], "animal", ["horse"],
        "death of the insured horse from accident, illness or disease",
        1000, 50000, 0, 350, 12, ["veterinary-health-certificate", "liveness-check"],
        "Sold direct by Ironclad. Needs a recent certificate from a vet."),
    # History: a product taken off the shelf. A consumer must not sell it.
    insurance_product(
        "wallet-theft-cover-launch-special", "Wallet Theft Cover, Launch Special",
        [EXCHANGE_SLUG], "asset", ["crypto-wallet"], WALLET_THEFT,
        100, 2000, 0, 10, 6, WALLET_COVER_CHECKS[:3],
        "A cut-price six-month cover the exchange ran when it first partnered "
        "with Ironclad. Withdrawn at the end of the promotion.",
        status="withdrawn", listed="2026-06-01", withdrawn="2026-08-31"),
    # Promised, not yet for sale.
    insurance_product(
        "vehicle-theft-cover", "Vehicle Theft Cover",
        [INSURER_SLUG], "asset", ["vehicle"],
        "theft of the insured vehicle",
        2000, 60000, 500, 480, 12, ["title-check", "identity-check"],
        "Announced for the new year. Not for sale yet.",
        status="announced", listed="2027-01-15"),
]

# The catalog's "today". Later than the wallets' asOf so the whole town is
# frozen at one moment.
CATALOG_AS_OF = "2026-11-25"

# A villain product uses the IDENTICAL shape and passes every shape rule.
# The fraud is in a claim the papers cannot back: it names Ironclad as its
# underwriter, and Ironclad's own storefront does not list it.
VILLAIN_PRODUCTS = [
    insurance_product(
        "VILLAIN--guaranteed-wallet-cover--names-an-underwriter-that-never-agreed",
        "Guaranteed Wallet Cover (no checks, instant)",
        ["VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry"],
        "asset", ["crypto-wallet"], WALLET_THEFT,
        100, 100000, 0, 5, 12, [],
        "Too good to be true: any amount, no checks, five dollars a year.",
        villain="Names Ironclad Insurance Group as underwriter, but Ironclad's "
                "storefront does not list this product; the seller is itself "
                "a villain whose EIN was never issued by the IRS registry"),
]

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
    # --- Lifecycle assortment (Aug 26, 2026 ideation session) -------------
    # Each of these assets exists to exercise ONE stage of the RWA lifecycle
    # at the gate. The story lives in ASSET_LIFECYCLES below; the full
    # hard-think is docs/LIFECYCLE_CATALOG.md §8.
    ("blackfeather-commissioned-mural", "'Dawn Over Quarry Road' commissioned mural panel",
     "artwork", "catalog-id", "TT-GFG-2026-0007", "sadie-blackfeather"),
    ("petrova-lakeside-cottage", "Petrova lakeside cottage, 9 Millpond Lane",
     "real-estate", "parcel-id", "TT-PARCEL-0221-033", "anya-petrova"),
    ("riverbend-quarry-warehouse", "Riverbend quarry-road warehouse (fractionalized)",
     "real-estate", "parcel-id", "TT-PARCEL-0917-201", "olaf-bjornsen"),
    ("quist-estate-grand-piano", "Quist estate 1962 concert grand piano",
     "instrument", "serial-number", "TT-PNO-1962-0448", "harold-quist"),
    ("hartmann-vintage-projector", "Hartmann restored 1948 carbon-arc cinema projector",
     "equipment", "serial-number", "TT-PRJ-1948-0112-R", "lena-hartmann"),
    ("mcbride-work-van", "McBride 2015 plumbing work van (total loss)",
     "vehicle", "vin", "1TTMC15X3FZ007733", "colin-mcbride"),
]

# ---------------------------------------------------------------------------
# ASSET LIFECYCLES — every asset is a lifecycle TEST VECTOR.
#
# WHY (teaching note): wallet systems die at the ENDS of lifecycles, not the
# beginnings. Each block below declares the stage an asset is frozen at, the
# plain-English story, and the behaviors the kernel gate MUST exhibit when
# this fixture is played through it ("kernelExpectations" become test
# assertions). Full reasoning: docs/LIFECYCLE_CATALOG.md.
# ---------------------------------------------------------------------------
ASSET_LIFECYCLES = {
    "heirloom-lange-1815-wristwatch": {
        "stage": "heirloom-in-family",
        "story": "In the Delgado family three generations; long provenance chain, "
                 "never sold at retail within living memory.",
        "kernelExpectations": [
            "long provenance chain verifies end-to-end from the head hash",
            "ownership provable in ZK without revealing the family history",
        ],
    },
    "morrow-family-farmhouse": {
        "stage": "homestead",
        "story": "Edgar Morrow's lifelong home; decades of inspection, repair, and "
                 "insurance records accrue in the asset's vault.",
        "kernelExpectations": [
            "thick vault stays fully private until a sale process begins",
            "records filed to the HOUSE convey; records about the OWNER never enter this vault",
        ],
    },
    "fairweather-pickup-truck": {
        "stage": "financed-with-lien",
        "story": "Amos financed the truck through Testtown Savings & Loan; the lien "
                 "is active until the loan is repaid.",
        "kernelExpectations": [
            "transfer attempts are REJECTED while the LienCredential is active",
            "'is this vehicle lien-free?' answers false in one bit, owner not revealed",
        ],
    },
    "zhao-grand-seiko-snowflake": {
        "stage": "clean-retail-purchase",
        "story": "Mei-Lin bought the watch new; provenance is a single retail block. "
                 "The happy path every other fixture complicates.",
        "kernelExpectations": [
            "unencumbered transfer succeeds and appends exactly one provenance block",
        ],
    },
    "blackfeather-commissioned-mural": {
        "stage": "creation",
        "story": "Commissioned through the Gilded Frame gallery and completed this "
                 "year; the artist's attestation is provenance block #1 — the asset "
                 "DIDz is minted at the moment of making.",
        "kernelExpectations": [
            "registration ceremony mints a permanent asset identity with creator attestation",
            "creator is the first trusted attester in the provenance chain",
        ],
    },
    "petrova-lakeside-cottage": {
        "stage": "mid-sale-escrow",
        "story": "Anya is selling; Marcus Reid prequalified and paid a deposit held "
                 "in escrow. The tiered disclosure ladder is LIVE: public sees a "
                 "price band, prequalified buyers see the address, the escrowed "
                 "buyer sees inspection history — and nobody sees Anya's personal "
                 "records, which were never filed in the house's vault.",
        "kernelExpectations": [
            "EscrowCredential unlocks deeper history tiers at query time",
            "same query returns different visibility per caller authority (spec §6.5)",
            "seller-personal records are absent from the asset vault by construction",
        ],
    },
    "riverbend-quarry-warehouse": {
        "stage": "fractionalized",
        "story": "Olaf (managing shareholder), Priscilla Vance, and Victor Osei hold "
                 "50/30/20 shares as credentials over ONE asset DIDz — shares are "
                 "credentials, not sub-entities (RWAz ruling: no entity explosion).",
        "kernelExpectations": [
            "many share-credentials bind to a single permanent asset identity",
            "'do I hold at least N shares?' provable without revealing total holdings",
        ],
    },
    "quist-estate-grand-piano": {
        "stage": "inherited",
        "story": "Harold inherited the piano when his mother Ingrid passed in 2024; "
                 "her DIDz is deceased (terminal) and the executor-authorized estate "
                 "transfer is the latest provenance block.",
        "kernelExpectations": [
            "deceased owner triggers succession, never a transfer FROM the terminal identity itself",
            "executor authority (a scoped grant) signs the estate transfer",
            "provenance records the succession without exposing the estate's private details",
        ],
    },
    "hartmann-vintage-projector": {
        "stage": "restored-re-anchored",
        "story": "Lena restored the projector; the corroded serial plate was replaced "
                 "during restoration (new anchor value ends in -R). Ship of Theseus: "
                 "identity survives an AUTHORIZED re-anchor ceremony with a qualified "
                 "attester; an unauthorized anchor change is presumptive fraud.",
        "kernelExpectations": [
            "authorized re-anchoring updates the binding and appends a provenance block",
            "the asset DIDz is unchanged across the anchor replacement",
        ],
    },
    "mcbride-work-van": {
        "stage": "destroyed",
        "story": "Totaled in 2025; Ironclad Insurance (adjuster: Theo Brandt) settled "
                 "the claim — the settlement is the FINAL provenance block. Terminal "
                 "means terminal: a salvage rebuild would be a NEW asset DIDz "
                 "carrying a salvage-history credential pointing at this one.",
        "kernelExpectations": [
            "all transfer attempts on a destroyed asset are rejected forever",
            "the vault becomes a read-only archive; history remains verifiable",
        ],
    },
}

# Villain assets: identical schema, fraud in the details (iron rule #2).
# NOT linked into any citizen's household — a fraudulent claim of ownership
# must never appear in an authentic citizen's dossier.
# slug, name, kind, anchor-kind, anchor, claimed-owner-description, fraud
VILLAIN_ASSETS = [
    ("VILLAIN--phantom-1815-wristwatch--serial-cloned-from-registered-heirloom",
     "Counterfeit 1815-style wristwatch presenting a cloned serial",
     "watch", "serial-number", "TT-1815-004417",
     "presented by an unregistered seller claiming clear title",
     "identity anchor TT-1815-004417 is CLONED from the registered "
     "heirloom-lange-1815-wristwatch; the registry already binds that serial "
     "to an existing asset DIDz — first-registered wins, the clone is refused"),
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
        **o["extra"],
        "operator": ({"walletCard": f"utils_Midnight/preProd-Wallets/wallets/wallet-{lady}.md",
                       "preprodAddress": LADIES[lady]} if lady
                      else {"walletCard": wallet_card(o["slug"]),
                            "preprodAddress": wallet_address(o["slug"]),
                            "note": "headless derived key; seed in the local-only vault"}
                      if o["slug"] in WALLETS
                      else {"walletCard": None, "preprodAddress": None,
                            "note": "bulk org — headless derived key planned"}),
    })

def multisig_wallet_dossier(slug, name, owner_fields, threshold, signers, story):
    """A crypto-wallet asset controlled by several keys. Signers are real
    pre-prod addresses; the account itself is a placeholder (see EXCHANGE notes)."""
    assert 1 <= threshold <= len(signers), slug
    write_json(os.path.join(ROOT, "dossiers", "assets", slug, "dossier.json"), {
        "schema": "testtown/dossier/v0.1", "category": "asset", "slug": slug,
        "displayName": name,
        "honesty": {"role": "AUTHENTIC", "fraudMechanism": None},
        "assetKind": "crypto-wallet",
        "identityAnchor": {"kind": "wallet-address", "value": None, "status": "PLACEHOLDER"},
        **owner_fields,
        "custody": {
            "model": "multi-sig",
            "threshold": threshold,
            "signerCount": len(signers),
            "signers": [{"role": role, "heldBy": held_by,
                          "preprodAddress": wallet_address(key_slug),
                          "walletCard": wallet_card(key_slug)}
                         for role, held_by, key_slug in signers],
            "assetCustody": None,
            "story": story,
        },
        "holdings": {"chain": "midnight", "network": "preprod", "balanceUsd": None,
                      "asOf": "2026-11-25", "evidence": "MOCK", "fictional": True},
        "placeholders": MULTISIG_PLACEHOLDERS,
        "papers": [], "documents": [],
    })

def product_dossier(p):
    """Write one product: a plain-English product sheet, then the dossier
    that commits to it by hash (the same pattern as an organization's charter)."""
    d = os.path.join(ROOT, "dossiers", "products", p["slug"])
    os.makedirs(d, exist_ok=True)
    sheet = os.path.join(d, "product-sheet.md")
    with open(sheet, "w") as f:
        f.write(f"# Product sheet: {p['name']}\n\n"
                f"- Covers: {', '.join(p['covers']['kinds'])} ({p['covers']['dossierCategory']})\n"
                f"- Against: {p['peril']}\n"
                f"- Amount: ${p['low']:,} to ${p['high']:,}\n"
                f"- Deductible: ${p['deductible']:,}\n"
                f"- Price: ${p['premium']:,} a year, {p['months']}-month term\n"
                f"- Buyer must clear: {', '.join(p['requires']) or 'nothing'}\n\n"
                f"{p['story']}\n\n"
                f"*(TestTown fixture document. Invented placeholder terms; its "
                f"sha256 is the dossier's commitment.)*\n")
    write_json(os.path.join(d, "dossier.json"), {
        "schema": "testtown/dossier/v0.1",
        "category": "product",
        "slug": p["slug"],
        "displayName": p["name"],
        "honesty": {"role": "VILLAIN" if p["villain"] else "AUTHENTIC",
                     "fraudMechanism": p["villain"]},
        "productKind": "insurance",
        "underwriterOrganizationSlug": p["underwriter"],
        "sellerOrganizationSlugs": p["sellers"],
        "availability": {"status": p["status"], "listedAt": p["listed"],
                          **({"withdrawnAt": p["withdrawn"]} if p["withdrawn"] else {}),
                          "asOf": CATALOG_AS_OF},
        "insurance": {
            "covers": p["covers"],
            "peril": p["peril"],
            "coverageUsd": {"min": p["low"], "max": p["high"]},
            "deductibleUsd": p["deductible"],
            "premiumUsdPerYear": p["premium"],
            "termMonths": p["months"],
            "requires": p["requires"],
        },
        "story": p["story"],
        "evidence": "MOCK",
        "fictional": True,
        "documents": [{"file": "product-sheet.md", "kind": "product-sheet",
                        "sha256": sha256_file(sheet),
                        "confirmableBy": f"dossiers/organizations/{p['underwriter']}/dossier.json"}],
    })

def main():
    all_orgs = ORGS + EMPLOYERS + EXCHANGES + VILLAINS

    # --- storefronts: which organization underwrites and sells what ---------
    # Derived from the PRODUCTS table so a product and its shop can never
    # disagree. Villain products are left out ON PURPOSE: the honest
    # underwriter not listing a product is exactly how the fraud is caught.
    storefronts = {}
    for p in PRODUCTS:
        storefronts.setdefault(p["underwriter"], {"underwrites": [], "sells": []})["underwrites"].append(p["slug"])
        for seller in p["sellers"]:
            storefronts.setdefault(seller, {"underwrites": [], "sells": []})["sells"].append(p["slug"])
    for o in all_orgs:
        if o["slug"] in storefronts:
            o["extra"] = {**o["extra"], "storefront": storefronts[o["slug"]]}

    # --- registries (the authorities of record) ---
    eins, regs = {}, {}
    for o in ORGS + EMPLOYERS + EXCHANGES:
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

    # The exchange's multi-sig wallets (written before the household scan
    # below so a customer's custody wallet shows up in their household).
    multisig_wallet_dossier(
        EXCHANGE_TREASURY_WALLET, "Quarry Street Exchange corporate treasury wallet",
        {"ownerOrganizationSlug": EXCHANGE_SLUG}, 2,
        [("treasury-signer", f"{name} ({role})", f"{EXCHANGE_SLUG}--treasury-signer-{i}")
         for i, (name, role) in enumerate(EXCHANGE_OFFICERS, start=1)],
        "The exchange's own money. Any two of the three officers must approve a "
        "movement, so no single officer can empty the treasury.")
    citizen_names = {c[0]: c[1] for c in CITIZENS}
    for customer, wallet_slug in EXCHANGE_CUSTOMER_WALLETS.items():
        multisig_wallet_dossier(
            wallet_slug, f"{citizen_names[customer]}'s custody wallet at Quarry Street Exchange",
            {"ownerCitizenSlug": customer, "custodianOrganizationSlug": EXCHANGE_SLUG}, 2,
            [("customer", citizen_names[customer], customer),
             ("exchange-cosigner", "Quarry Street Exchange (custody desk)",
              f"{EXCHANGE_SLUG}--custody-cosigner"),
             ("recovery-trustee", "TestTown Savings & Loan", EXCHANGE_RECOVERY_TRUSTEE)],
            "Funds the exchange holds for a customer. Any two of the three "
            "signers must approve, so the exchange cannot move them alone.")

    # Hand-authored dossiers (not in the tables above) also belong to a
    # household. Scan the disk so regenerating never drops them: the insured
    # wallets from the intents layer and the lifecycle fixtures live this way.
    table_assets = {a[0] for a in ASSETS}
    table_animals = {a[0] for a in ANIMALS}
    for kind, owner_key, known in (("assets", "ownerCitizenSlug", table_assets),
                                   ("animals", "custodianCitizenSlug", table_animals)):
        folder = os.path.join(ROOT, "dossiers", kind)
        for slug in sorted(os.listdir(folder)):
            path = os.path.join(folder, slug, "dossier.json")
            if slug in known or not os.path.exists(path):
                continue
            with open(path) as f:
                owner = json.load(f).get(owner_key)
            if owner in citizens_with_household and slug not in citizens_with_household[owner][kind]:
                citizens_with_household[owner][kind].append(slug)

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
            "operator": ({"note": "Citizens hold their OWN keys — self-sovereign. "
                                   "The seed is in the local-only vault, never here.",
                           "walletCard": wallet_card(slug),
                           "preprodAddress": wallet_address(slug)}
                          if slug in WALLETS else
                          {"note": "Citizens hold their OWN keys — self-sovereign; "
                                   "wallet assignment lands with the admission-gate build."}),
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
            # Optional v0.2 extension: the lifecycle test vector this asset
            # embodies (docs/LIFECYCLE_CATALOG.md §8, §11).
            **({"lifecycle": ASSET_LIFECYCLES[slug]} if slug in ASSET_LIFECYCLES else {}),
        })

    # Villain assets: same shape as authentic ones, fraud named verbosely.
    # No ownerCitizenSlug — a fraudulent ownership claim never touches an
    # authentic citizen's household; the claim text lives in the dossier.
    for slug, name, kind, anchor_kind, anchor, claimed, fraud in VILLAIN_ASSETS:
        write_json(os.path.join(ROOT, "dossiers", "assets", slug, "dossier.json"), {
            "schema": "testtown/dossier/v0.1", "category": "asset", "slug": slug,
            "displayName": name,
            "honesty": {"role": "VILLAIN", "fraudMechanism": fraud},
            "assetKind": kind,
            "identityAnchor": {"kind": anchor_kind, "value": anchor},
            "claimedOwnership": claimed,
            "papers": [], "documents": [],
            "lifecycle": {
                "stage": "fraud-cloned-anchor",
                "story": claimed,
                "kernelExpectations": [
                    "duplicate identity anchor is detected against the registry",
                    "registration of the clone is REFUSED; the fixture reads as an alarm if admitted",
                ],
            },
        })

    for p in PRODUCTS + VILLAIN_PRODUCTS:
        product_dossier(p)

    print(f"generated: {len(all_orgs)} organizations ({len(VILLAINS)} villains), "
          f"{len(CITIZENS)} citizens, {len(ANIMALS)} animals, "
          f"{len(ASSETS)} assets (+{len(VILLAIN_ASSETS)} villain assets), "
          f"{len(PRODUCTS)} products (+{len(VILLAIN_PRODUCTS)} villain product)")

if __name__ == "__main__":
    main()
