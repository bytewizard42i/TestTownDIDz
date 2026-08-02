# TestTownDIDz 🏙️

> **The world BEFORE the trust system.**
>
> **Status**: Founding docs + exemplar dossiers (Aug 2, 2026). Population
> build-out in progress.
> **Stage**: DemoLand asset base → TestWired API base
> (see `DIDzMonolith-docs/standards/BUILD_STAGES.md`)
> **License**: Apache-2.0

## What TestTown is

TestTown is the DIDzM ecosystem's **test population**: a small American
town's worth of organizations, citizens, animals, and assets — each carried
by a **dossier**, a folder of evidence with provenance, exactly like the
paper trail a real entity accumulates before any blockchain exists.

TestTown deliberately lives **outside** the DIDz system and never imports
DIDz code. That separation is the whole point:

```
TestTown (reality)                    DIDz.io (the gate)
──────────────────                    ─────────────────────────
organizations with paper   ──apply──▶ onboarding review:
trails: EIN, articles of              cross-check dossier against
incorporation, licenses               TestTown's authorities of record
                                        │
citizens, animals, assets             accepted → org DIDz minted →
with their own dossiers               TrustedIssuerRegistry enrollment
                                        │
IMPOSTORS with forged or              issuer attests citizens, agents,
dangling credentials       ──apply──▶ animals, RWAs through the app
                                        │
                                      impostors: ★ REJECTED ★ (tested!)
```

## Why the gate matters (the threat model in one paragraph)

The worst possible failure of the DIDzM ecosystem is a **fraudulent trusted
issuer**: a fake DMV doesn't forge one credential, it mints *unlimited
legitimate-looking* credentials — a duplicate root of trust and a vector
for massive fraud. So issuer admission is the most security-critical
ceremony in the system, and TestTown exists to test it honestly: with
authentic applicants that must be ADMITTED and deliberate impostors that
must be REFUSED. See `docs/THREAT_MODEL.md`.

## The dossier model

A **dossier** is not a database row. It is a folder of evidence:

- `dossier.json` — the structured summary (who, what, identifiers, keys)
- document files — articles of incorporation, licenses, certificates
  (markdown standing in for PDFs; each is content-hashed so on-chain
  attestations have something real to commit to)
- every claim in the summary points at the document that supports it and
  the **authority of record** that can confirm it

Full schema: `docs/DOSSIER_SCHEMA.md`.

## Authorities of record (what makes "verified" mean something)

Real-world vetting means calling the issuing authority: the IRS for an
EIN, the Secretary of State for a registration. TestTown therefore ships
those authorities as **mock registries** (`registries/`):

- `irs-ein-registry.json` — every EIN the "IRS" has actually issued
- `state-corporations-registry.json` — registrations, standing, officers

The DIDz.io onboarding gate cross-checks each application against these.
An impostor's dossier can be beautifully formatted — the registries are
what expose it. In DemoLand the registries are read as files; in TestWired
they are served as test HTTP APIs (planned: `registries/server`).

## Naming convention for nefarious actors (verbose and intuitive)

Every fraudulent resident is IMPOSSIBLE to mistake, in folder name and in
labels:

```
VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry/
VILLAIN--first-dmv-of-delaware--impersonates-dissolved-entity/
VILLAIN--evergreen-diploma-mill--accreditation-cites-nonexistent-board/
```

The `VILLAIN--<name>--<exact-fraud-mechanism>` pattern means a test that
accidentally ADMITS one reads as an alarm in any log or file listing.
Villains carry the same dossier structure as honest residents — the fraud
lives in the details, exactly as it does in life.

## Repo layout

```
dossiers/
  organizations/   hospitals, schools, DMV, SSA, vets, employers, ... + VILLAINs
  citizens/        ~20 residents with job histories pointing at the employers
  animals/         pets and horses (custodians point at citizens)
  assets/          watches, vehicles, real estate (owners point at citizens)
registries/        the authorities of record (mock IRS, State corporations)
docs/              DOSSIER_SCHEMA.md, THREAT_MODEL.md
```

## How the ecosystem consumes TestTown

- **DemoLand**: load dossiers/registries as files, play the world through
  the didz-kernel seams in memory.
- **TestWired**: same dataset; the admission ceremony and attestations run
  as REAL transactions on Midnight localnet/preprod, and registries are
  test APIs.
- **Operator keys**: featured organizations are operated ("possessed") by
  the named wallet roster in `utils_Midnight/preProd-Wallets/` (Sarah,
  Jessica, …); bulk employers derive keys headlessly. Seeds NEVER live in
  this repo — dossiers carry public keys/addresses only.

## House rules

1. TestTown never imports DIDz packages. Consumers import TestTown.
2. No secrets, ever — dossiers are public paper; keys are public halves.
3. Villains are permanent residents: removing one weakens the gate's tests.
4. All data is fictional; resemblance to real entities is coincidental.
```
