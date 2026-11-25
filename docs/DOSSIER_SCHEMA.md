# The Dossier Schema v0.1

> A **dossier** is a folder of evidence with provenance — the paper trail
> an entity accumulates in the world before any trust system exists. We
> chose the word deliberately over "object": an object is data; a dossier
> is *evidence*, each piece pointing at the document that carries it and
> the authority that can confirm it. This is a new schema for the world —
> convention is a starting point here, not a boundary.

## Anatomy

```
dossiers/<category>/<slug>/
  dossier.json          ← structured summary (below)
  <document>.md         ← the actual papers, one file each, content-hashed
```

## dossier.json — common spine (all categories)

```jsonc
{
  "schema": "testtown/dossier/v0.1",
  "category": "organization | citizen | animal | asset",
  "slug": "st-brigids-general-hospital",
  "displayName": "St. Brigid's General Hospital",
  "honesty": {
    // Verbose and intuitive, per John's ruling Aug 2 2026:
    "role": "AUTHENTIC" ,          // or "VILLAIN"
    "fraudMechanism": null         // villains: exact, human-readable, e.g.
                                   // "EIN is well-formed but was never
                                   //  issued by the IRS registry"
  },
  "documents": [
    {
      "file": "articles-of-incorporation.md",
      "kind": "articles-of-incorporation",
      "sha256": "<hash of the file>",
      "confirmableBy": "registries/state-corporations-registry.json"
    }
  ],
  "operator": {
    // Who may act as this entity ("possession"). PUBLIC halves only.
    "walletCard": "utils_Midnight/preProd-Wallets/wallets/wallet-sarah.md",
    "preprodAddress": "mn_addr_preprod1..."
  }
}
```

## Category extensions

### organization (prospective trusted issuer)
```jsonc
{
  "identifiers": {
    "ein": "12-3456789",                     // confirmable in the IRS registry
    "stateRegistration": "PA-C-0048291",     // confirmable in the State registry
    "founded": "1987-04-12"
  },
  "authority": {
    "issuerType": "hospital",                // hospital | school-k12 | college |
                                             // dmv | ssa | veterinary | mechanic |
                                             // employer | real-estate | appraiser
    "requestedAssuranceLevel": "REGULATED_ENTITY",  // maps to TrustedIssuerRegistry
    "attestationScopes": ["BIRTH_CERTIFICATE", "MEDICAL_RECORD"],
    "subjectTiers": ["human"],
    "licenses": [ /* documents[] entries: facility license, accreditation... */ ]
  },
  "officers": [{ "name": "...", "role": "Administrator", "citizenSlug": "..." }]
}
```

### citizen
`identifiers` (birth certificate doc, licenses held), `employment[]`
(employerSlug + role + dates — must point at organization dossiers),
`householdSlugs` (animals/assets custodied).

### animal
`species/breed`, `identityBinding` (microchip id document — the analog of
a biometric), `custodianCitizenSlug`, `careHistory[]` (vet visit documents).

### asset
`assetKind` (watch | vehicle | real-estate | artwork | instrument |
equipment ...), `identityAnchor` (serial number / VIN / parcel id document),
`ownerCitizenSlug`, `papers[]` (title, appraisal, service records).

**Optional `lifecycle` block (v0.2 candidate, Aug 26 2026):** every asset is
a lifecycle TEST VECTOR — the block declares which stage of an RWA's life the
fixture is frozen at, the plain-English story, and the behaviors the gate
must exhibit (`kernelExpectations` become test assertions). Villain assets
carry it too, with `claimedOwnership` in place of `ownerCitizenSlug` (a
fraudulent claim never touches an authentic citizen's household). Full
catalog and rationale: `LIFECYCLE_CATALOG.md`.

```jsonc
"lifecycle": {
  "stage": "mid-sale-escrow",        // stage name from LIFECYCLE_CATALOG.md §8
  "story": "…",                       // the situation, in plain English
  "kernelExpectations": ["…"]        // what the gate MUST do with this fixture
}
```

**Optional `intents` block (v0.2 candidate, Nov 24 2026):** an intent is a
WANT expressed about the asset — not a fact, not an outcome, never a gate
decision. It is a modular block any asset dossier can carry: the same shape
serves a wallet its owner wants insured today and a vehicle or deed tomorrow.
Outcomes always belong to the gatekeepers (oracles, registries, contracts);
TestTown only records what the world wanted before the trust system answered.

```jsonc
"intents": [
  // A generic intent: it can be about anything.
  {
    "wants": "Sell the piano before the estate sale",  // required, plain English
    "expressedAt": "2026-11-15",   // required: when the want was voiced
    "status": "open",              // required: open | accepted | withdrawn | expired
    "startDate": "2026-12-01",     // optional: when it should take effect
    "expiresAt": "2027-02-13",     // optional: unanswered past this, it is stale
    "story": "…"                 // optional: why, in plain English
  },

  // An insurance wish: a generic intent plus the insurance block.
  {
    "wants": "Insure this wallet for $5,000",
    "expressedAt": "2026-11-15",
    "startDate": "2026-12-01",     // REQUIRED for insurance wishes
    "expiresAt": "2027-02-13",     // REQUIRED for insurance wishes
    "status": "open",
    "story": "…",
    "category": "insurance",       // names the block below
    "insurance": {
      "wish": "cover-asset",       // the insurance wish, open vocabulary
      "coverageUsd": 5000          // what the owner asked for — may mismatch
                                   // the balance on purpose (people do that)
    }
  }
]
```

**Generic first, specific second.** The intent object is open: `wants`,
`expressedAt` and `status` are all it needs, so it can record any want about
any asset. `category` is optional. When present it names one extra block
holding the details of that kind of want; an unknown category is allowed and
its block is free-form. `insurance` is the first category with rules of its
own: an insurance wish must carry `startDate`, `expiresAt`, and an
`insurance` block with `wish` and a positive `coverageUsd`.

**Intents have a lifecycle.** A want is voiced (`expressedAt`), asks to take
effect on a `startDate`, and goes stale at `expiresAt` if nobody answers,
the way a quote does. `status` freezes the fixture at one stage:
`open` (live ask), `accepted` (the owner took an offer — still the owner's
act, not a gate verdict), `withdrawn` (the owner changed their mind), or
`expired` (ran out unanswered). An asset may carry several intents over
time; an expired one stays in the dossier as history, and a consumer MUST
NOT treat it as a live ask. "Now" for a fixture is the asset's
`holdings.asOf` date: an `open` intent has not passed its `expiresAt` as of
that date, an `expired` one has. `expiresAt` may fall before `startDate`
(an offer open through Dec 31 for a Jan 1 start).

**`crypto-wallet` assetKind + `holdings` block:** a wallet's identity anchor
IS its address (`kind: "wallet-address"`), the serial-number analog. The
balance is not identity — it is a temporal observation — so it lives in a
separate `holdings` block (`chain`, `balanceUsd`, `asOf`, `evidence: "MOCK"`),
in-world confirmable on-chain at the anchor. No keys exist; pretend wallets
need none, and the no-secrets rule is kept by construction.

## The three iron rules

1. **Every claim is confirmable or it is decoration.** Claims either cite a
   document in this dossier plus an authority of record, or they carry no
   evidentiary weight at the gate.
2. **Villains use the identical schema.** Fraud lives in the DETAILS
   (an EIN missing from the registry, a registration in DISSOLVED
   standing) — never in a different shape. The gate must work for its
   living.
3. **No secrets.** Public keys and addresses only; operator seeds live in
   the local-only wallet vault.
```
