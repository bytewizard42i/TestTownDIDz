# TestTownDIDz 🏙️

> **The world BEFORE the trust system.**
>
> **Status**: Founding docs + exemplar dossiers (Aug 2, 2026). Population
> build-out in progress.
> **Stage**: DemoLand asset base → TestWired API base
> (see `DIDzMonolith-docs/standards/BUILD_STAGES.md`)
> **License**: Apache-2.0

## 🗺️ A Visitor's Map of the DIDzM Ecosystem

*Every town needs a map on the welcome sign. TestTown is where the whole
DIDzMonolith comes to be tested — so here is the whole town it belongs
to, laid out the way the trust kernel sees it: six civic functions that
every working society (and every working identity system) must staff.*

### The Town Charter — the DIDz Trust Kernel

**[didz-kernel](https://github.com/bytewizard42i/DIDzMonolith/tree/main/didz-kernel)**
is the constitution everything else swears to: the **DIDz Protocol v0.1**
(RFC-style spec, DIF/W3C introduction letters drafted), five provider
seams, an orchestrator, and a conformance suite that IS the law — any
backend that passes it is a lawful citizen. Shipped and green:
`kernel-types` · `kernel-core` · `kernel-demoland` (MOCK reference) ·
`kernel-conformance` · `adapter-midnight` (real circuits, both pillars) ·
`adapter-midnight-localnet` (REALDEAL_TEST on a live network) ·
**`@didz/wallet`** — the seven-tier Tiered Wallet (humans, agents,
organizations, animals, devices, locations, objects/RWAs).

### The Six Civic Functions

| Civic function | "Who staffs it in a town" | Repo | Honest status (Aug 2, 2026) |
|---|---|---|---|
| **Identity** — WHO exists | The records office | [DIDz-io](https://github.com/bytewizard42i/DIDz_io) | `DIDzRegistry` (17 circuits) + `TrustedIssuerRegistry` (11) verified on compactc 0.31.1; **deployed on a live Midnight network with real ZK proofs**; preprod in flight |
| **Authority** — WHAT may act, within what bounds | The commissioner of permits | [AgenticDID](https://github.com/bytewizard42i/AgenticDID_io_me) | Scoped-grant delegation REAL (midnight-modules `scoped-grant`, TestWired in-process); the flashy web demo is honest DemoLand (MOCK) |
| **Objects** — WHAT things exist, who holds title | The county clerk (deeds & titles) | [RWAz](https://github.com/bytewizard42i/RWAz) | `rwa_registry` — **first DIDzM contract ever on a live chain**: VIN-model identity, movable title, liens, provenance chain, ZK proof-of-ownership |
| **Data** — WHAT data, served at what tier | The librarian who checks your card | [HelixCTW](https://github.com/bytewizard42i/HelixCTW) | CockroachDB cluster + Bedrock agent + tiered gating live (hackathon build); kernel `DataGateway` adapter planned |
| **Enforcement** — is THIS action allowed right now? | The gatehouse | taskFence_Ai | ⛔ **FROZEN** (OpenAI hackathon hold) — kernel expresses the concept natively meanwhile |
| **Observation** — who's watching the watchers | The night watchtower | [ZKSplunk](https://github.com/bytewizard42i/ZKSplunk_Splunking_w_Midnight) / PrivateEye | Splunk forwarding + dashboards built; vitals implementation lives in the ZKSplunk fork |

### The Town Services

| Service | Repo | What it does |
|---|---|---|
| 🏥 **The clinic** | [MidnightVitals](https://github.com/bytewizard42i/MidnightVitals) | `@midnight-vitals/core` + `vitals` CLI — headless health probes (node, indexer, proof server, toolchain, Docker, on-chain address) for ANY project; React panel + MCP wrapper planned |
| ⚙️ **The power plant** | midnight-modules | 16 engine contracts (scoped-grant, pol-credential, human-credentials, recovery-core…) — the shared circuits products compose |
| 🚉 **The train to the real world** | midnight-local-dev | One-command local Midnight network (node 1.0.0 / indexer 4.3.3 / proof-server 8.1.0) — where TestWired begins |
| 🏙️ **This repo** | TestTownDIDz | The test population: dossiers, authorities of record, villains |
| 💰 **The bank vault** | `utils_Midnight/preProd-Wallets` (local-only) | Ten named operator wallets (Sarah…Greta), seeds in `tdust-secrets/`, never in git |
| 📚 **Reference library** | utils_midnight-expert (official!) + Kapa MCP | Source-of-truth for Compact/Midnight; the deprecated Idris MCP retired with honors |

### The Neighborhoods (products that consume the kernel)

**Identity-first:** KYCz · selectConnect (first paying product) · ProMingle
· SouLink · onlyHumans · realVote · SentinelDID — **Assets & lineage:**
petProData · equineProData · LegacyKey (estate flows; localnet-deployed,
45 tests) · SilentLedger · CryptoSure — **Data & discovery:**
DiscoveryManagement (Vegas Summit demo) · safeHealthData · sharedScience —
**and ~30 more** in the [monolith](https://github.com/bytewizard42i/DIDzMonolith),
plus five books.

### The Town Laws (conventions every repo obeys)

1. **Build stages**: DemoLand → TestWired → RealDeal
   (`DIDzMonolith-docs/standards/BUILD_STAGES.md`)
2. **Evidence labels**: every output declares `MOCK` / `REALDEAL_TEST` /
   `REALDEAL` / `PLANNED` — a demo must never be mistakable for a proof
3. **Identity is never a token**: no transfer circuits exist, by
   construction; keys rotate, identity stays
4. **Privacy by default**: commitments on-chain, facts with the holder,
   one-bit disclosures on demand
5. **Issuer admission is sacred**: the gate cross-checks dossiers against
   authorities of record — and TestTown's villains keep it honest

---

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

## Future districts (ideas parked, not promised)

- **Midnight City integration** 🌃 (John, Aug 2 2026): [midnight.city](https://www.midnight.city/)
  is the OFFICIAL Midnight ecosystem's persistent AI-agent world (dcSpark +
  IO, on Midnight L2) — thousands of autonomous agents with professions,
  factions, and (per their roadmap) their own wallets "to trade, pay, and
  earn on your behalf. Privately." Ambition: offer **Citizen DIDz** —
  agent-tier DIDz custodied by owners, scoped grants (two-cap bounded
  spending) governing agent wallets, faction/profession attestations
  provable in ZK. See `AgenticDID/docs/MIDNIGHT_CITY_INTEGRATION_BRIEF.md`.
- **Test-agent module** (the earlier riff worth keeping under another
  name): a sibling module of autonomous test agents — the verbs to
  TestTown's nouns — including ADVERSARIAL agents (cap-probing, proof
  replay, post-admission scope creep) chaos-testing the kernel's
  enforcement and budget mechanics. Iron rule if built: it READS TestTown,
  never writes it.
