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
