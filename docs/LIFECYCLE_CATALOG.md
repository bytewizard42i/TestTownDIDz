# The Lifecycle Catalog

> **Every kind of resident, from first breath to last receipt.**
>
> **Status:** IDEATION → fixture design (Aug 26, 2026 session: soul-bound
> wallets, traveling asset vaults, lifecycle hard-think — John + Penny 🎀)
> **Companion to:** `DOSSIER_SCHEMA.md`, `THREAT_MODEL.md`, and the DIDz
> Protocol v0.1 spec (`didz-kernel/FORMAL_SPECS_W3C_DIF/didz-protocol-v0.1.md`)
>
> **Why this document exists:** wallet architectures die at the ENDS of
> lifecycles, not the beginnings. "Create" is easy and everyone designs for
> it; "merge," "inherit," "dissolve," "total," and "die" are hard and
> everyone punts. TestTown's job is to make sure the DIDzM gate has already
> met every one of these situations before the real world brings them.

---

## 1. The kernel's lifecycle vocabulary (what we build on)

The DIDz Protocol (spec §4.2) gives every identity exactly six statuses:

```
active ⇄ suspended        (recoverable; the entity still exists)
active → retired          (recoverable in principle; wound down on purpose)
active → deceased         (TERMINAL — humans and animals)
active → dissolved        (TERMINAL — organizations, governments, agencies)
active → destroyed        (TERMINAL — objects, devices, RWAs)
```

Three iron consequences, already normative in the spec:

1. **There is no `expired`.** Identity never expires; only credentials do.
2. **Terminal is terminal.** No transition out — ever. A "revived" business
   is a NEW identity that *references* the old one; it is not the old one.
3. **History survives death.** Receipts, provenance chains, and the identity
   record itself remain verifiable forever. Erasure applies to holder-side
   private facts, never to the fact that an entity existed and acted.

The rest of this document walks every kind of TestTown resident through its
whole life and asks: does the vocabulary hold? Where it strains, we mark an
**OPEN RULING** for John rather than inventing protocol semantics silently.

---

## 2. Humans (citizens)

```
birth ──▶ active ⇄ suspended (court order? incapacity?) ──▶ deceased (terminal)
            │
            ├─ POL credentials renew liveness (identity itself never expires)
            ├─ keys rotate on compromise; m-of-n social recovery
            └─ credentials attach/expire/revoke continuously (the living folder)
```

- **Where the model is strongest.** It was designed for humans: POL handles
  "alive as of," rotation handles compromise, the soul-bound rule handles theft.
- **Where it strains — death is not an event, it is a CASCADE.** A deceased
  citizen was probably: custodian of animals, devices, agents, and asset
  vaults; grantor of live scoped grants; holder of title credentials.
  Every one needs a destination:

  | The deceased held... | What must happen |
  |---|---|
  | Custody of animals/devices/assets | Governed **succession ceremony** → new custodian (LegacyKey's dead-man's-switch is the trigger; heirs receive custody) |
  | Title credentials | Estate transfer — title moves via the normal transfer circuit, executor-authorized |
  | Live grants issued TO others | **Revocation-on-death cascade** — a dead grantor's authority slices must die with them (spec §5.4 cascade, triggered by lifecycle) |
  | Live grants held FROM others | Auto-void: the actor is no longer `active`, gate denies (`actor-not-active`) |
  | Private wallet contents | Heir handoff per LegacyKey; un-bequeathed raw facts are **erased by default** (privacy default outlives the person) |

- **OPEN RULING (R1):** does `deceased` auto-cascade-revoke all grants the
  deceased ISSUED, or do some survive (e.g. a standing grant to a caretaker
  feeding the horse until succession completes)? Proposal: revoke all, but the
  succession ceremony may issue bridge grants under executor authority.
- **TestTown fixtures:** every citizen; the estate path is exercised by
  `quist-estate-grand-piano` (inherited asset, see §8).

## 3. Businesses (organizations)

```
founding ──▶ active ⇄ suspended (license lapse, receivership)
                │
                ├──▶ retired (voluntary wind-down; obligations settled)
                └──▶ dissolved (terminal)
```

The interesting cases are the ones with no human analog:

- **Merger/acquisition.** Identity is soul-bound for orgs too — an acquired
  company's DIDz is NOT transferred to the buyer (no transfer op exists).
  What actually happens: the acquired org's *assets* transfer title, its
  *issuer authority* is re-attested or retired, and its DIDz goes `dissolved`
  (or survives as a subsidiary, still `active`, with new officers = key
  rotation). The "company" that survives a merger is whichever DIDz stayed
  active. **OPEN RULING (R2):** should a dissolved-by-merger org record carry
  a successor pointer (a commitment to the surviving DIDz) so old credentials
  can be traced forward?
- **Issuer death ≠ credential death.** When a trusted issuer dissolves, the
  credentials it issued MUST remain verifiable (the hospital that recorded
  your birth closing does not un-birth you). Issuer status gates NEW
  issuance, never old verification. The TrustedIssuerRegistry's
  suspend/reactivate already points this way.
- **Zombie fraud.** Impersonating a dissolved entity is TestTown's villain
  #2 (`VILLAIN--first-dmv-of-delaware--impersonates-dissolved-entity`). The
  lifecycle registry IS the defense: `DISSOLVED` standing in the authority
  of record defeats a beautiful dossier.
- **TestTown fixtures:** all organizations; the zombie villain; the
  registries' `standing` field.

## 4. Governments

```
constitution ──▶ active  (essentially immortal by design)
                   │  officers/administrations rotate = KEY ROTATION writ large
                   │  the government's DIDz never changes across elections
                   └──▶ dissolved (rare, historic: succession of states)
```

- **The deep insight: an election is a key rotation.** The government's
  identity persists; its *controlling keys* (officers) change on schedule.
  This is exactly spec §4.3 — identity never moves, keys rotate — applied at
  civilization scale. No new machinery needed.
- **Continuity of obligations.** Credentials issued under administration N
  MUST verify under administration N+1 — same DIDz, higher key epoch. The
  key-epoch counter in the identity record is the audit trail of
  administrations.
- **Succession of states** (annexation, secession, reorganization) is the org
  merger problem at maximum stakes — R2's successor pointer matters most here.
- **TestTown fixtures:** implicit in the Commonwealth DMV and SSA field
  office being *offices of* larger governments (see §5).

## 5. Government agencies

```
created by statute ──▶ active ⇄ suspended (funding lapse, shutdown!)
                         │──▶ renamed/reorganized  (key rotation + credential re-scope,
                         │                          NOT a new identity... usually)
                         └──▶ abolished → dissolved (terminal, successor pointer)
```

- Agencies are the entity kind that gets **renamed, merged, and split** most
  often. The test: did the legal person persist? If the statute renames an
  agency, same DIDz (a name was never in the identity record anyway — names
  are credentials!). If a statute abolishes one agency and creates another
  with similar duties, that is dissolution + fresh registration + successor
  pointer.
- **A government shutdown is `suspended`, not `dissolved`** — recoverable,
  and grants issued by the agency may be configured to survive suspension
  (checks keep clearing) while new issuance halts. **OPEN RULING (R3):**
  default behavior of grants whose GRANTOR is suspended — freeze or persist?
  Proposal: persist (revocation stays available), because suspension of the
  grantor shouldn't strand every downstream actor mid-action.
- **Delegated sovereignty.** An agency's issuer authority is itself a scoped
  grant from its government — attenuation-only delegation, at law. A DMV
  office attests driver's licenses because the Commonwealth granted it that
  scope and nothing more. The kernel's grant machinery models
  inter-governmental delegation with zero new concepts.
- **TestTown fixtures:** `commonwealth-dmv-testtown-office` and
  `testtown-social-security-field-office` — both are LOCAL OFFICES holding
  attenuated authority from larger sovereigns.

## 6. Institutions (hospitals, schools, colleges, banks)

```
chartered ──▶ active ⇄ suspended (accreditation lapse, license revocation)
                │──▶ retired  (teaching hospital winds down; records custodian named)
                └──▶ dissolved (terminal; RECORDS OUTLIVE THE INSTITUTION)
```

- Institutions are organizations whose *issuer role dominates*: their
  lifecycle events primarily threaten OTHER people's credentials.
- **Accreditation is the institution's POL.** A school does not expire; its
  *accreditation credential* renews, and verifiers choose the freshness
  window they accept (spec §6.3, applied to orgs). A diploma from a college
  accredited *at the time of issuance* stays provable forever — the
  attestation binds "accredited-as-of," not "accredited-now."
- **The records-custody problem.** When St. Brigid's dissolves, who answers
  birth-record confirmations? Real law appoints a records custodian;
  DIDzM's answer is better — the ATTESTATION already on-chain needs no
  living issuer to verify, and the holder keeps the raw facts. Dissolution
  costs future issuance, not past truth.
- **The diploma-mill villain** (`VILLAIN--evergreen-diploma-mill--…`) is the
  lifecycle fraud inverse: an institution that never validly ENTERED the
  issuer lifecycle (accreditor doesn't exist).
- **TestTown fixtures:** St. Brigid's, the Maple Hollow schools, Keystone
  Ridge College, Testtown Savings & Loan, the diploma mill.

## 7. Agents (AgenticDID) — personal and service

```
spawned (permissionless!) ──▶ active ⇄ suspended (custodian pauses it)
        custodian = human      │ lives ENTIRELY inside scoped grants:
        (personal) or org      │ two caps, expiry, attenuation, cascade
        (service)              └──▶ retired (decommissioned; receipts persist)
```

- Agents are the CHEAPEST and most NUMEROUS identities — spawned by the
  thousand, retired by the thousand. Design consequences:
  - `retired`, not `deceased` — decommissioning is administrative, and the
    receipts trail is the part that must outlive the agent (accountability
    was the whole point).
  - Agent "death" is undramatic BY DESIGN: revoke its grants (cascade takes
    sub-agents with it), mark retired, done. Nothing to inherit — an agent
    OWNS nothing; it only ever held authority slices.
- **OPEN RULING (R4) — the model-upgrade question:** when the underlying
  model/runtime of an agent changes (GPT-N → GPT-N+1, new attested build),
  is that a key rotation (same agent DIDz, new epoch, continuous receipts)
  or a new agent (fresh DIDz, fresh trust)? Proposal: custodian's choice,
  but ATTESTED either way — a runtime-attestation credential pins what the
  agent is made of, and verifiers can demand freshness. A silently swapped
  brain behind a trusted DIDz is the agent version of the zombie villain.
- **Suspension is the custodian's pause button** and should be instant,
  unilateral, and cheaper than revocation (grants survive suspension frozen,
  resume on reactivation) — because "I'm not sure, stop everything" must be
  the easiest action in the whole system.
- **TestTown fixtures:** none yet — agents are the *verbs* to TestTown's
  nouns and belong to the planned test-agent module (README "future
  districts"). This catalog defines the lifecycle they will exercise.

## 8. RWAs and objects — where lifecycle gets a BODY

Objects obey the VIN invariant (RWAz `ARCHITECTURE.md`): **asset identity is
permanent; ownership, encumbrance, and custody move around it.** The asset
carries its own vault (folders: title, provenance, encumbrances, appraisals)
that TRAVELS with it across owners — access rotates at transfer; the records
never move. Each lifecycle stage below now has a named TestTown fixture:

| Stage of life | What it tests at the gate | TestTown fixture |
|---|---|---|
| **Creation** — identity minted at the moment of making, creator's attestation is provenance block #1 | registration ceremony; creator-as-first-issuer | `blackfeather-commissioned-mural` |
| **Clean retail purchase** — short provenance, no encumbrance | happy-path transfer | `zhao-grand-seiko-snowflake` |
| **Financed** — active lien; sale blocked until release | encumbrance-blocked transfer circuit | `fairweather-pickup-truck` (lien: Testtown Savings & Loan) |
| **Mid-sale escrow** — deposit paid, tiered disclosure ladder live | EscrowCredential unlocks deeper history tiers; prequalified-buyer gating | `petrova-lakeside-cottage` (buyer: marcus-reid, deposit escrowed) |
| **Fractionalized** — many share-credentials over ONE asset DIDz (no entity explosion) | share registry; prove ≥N shares without revealing holdings | `riverbend-quarry-warehouse` (3 shareholders) |
| **Inherited** — owner deceased; estate succession ceremony | terminal-status cascade → executor-authorized title transfer | `quist-estate-grand-piano` |
| **Heirloom in-family** — multi-generation provenance, high sentimental/monetary value | long provenance chains; recovery-grade custody | `heirloom-lange-1815-wristwatch` |
| **Homestead** — decades of records accrue on one asset | thick vault, selective disclosure at eventual sale | `morrow-family-farmhouse` |
| **Restored / re-anchored** — the physical anchor itself was replaced (Ship of Theseus) | identity survives anchor REBINDING only via authorized ceremony + provenance entry | `hartmann-vintage-projector` (serial plate replaced during restoration) |
| **Destroyed** — totaled, written off | TERMINAL status; all future transfers rejected forever; insurance settlement is the last provenance block | `mcbride-work-van` (total loss, Ironclad claim) |
| **Fraud: cloned anchor** — a forged twin claims a registered serial | duplicate-anchor detection; first-registered wins; the clone is refused | `VILLAIN--phantom-1815-wristwatch--serial-cloned-from-registered-heirloom` |

- **OPEN RULING (R5) — re-anchoring.** Proposal: the identity anchor
  (VIN/serial/parcel) is *evidence of* identity, not identity itself; an
  authorized re-anchor ceremony (owner + qualified attester, e.g. the
  horologist/mechanic) updates the binding and appends provenance. An
  UNAUTHORIZED anchor change is presumptive fraud — exactly what the
  phantom-watch villain probes from the other side.
- **OPEN RULING (R6) — salvage resurrection.** A "destroyed" van rebuilt
  from salvage: terminal means terminal, so the rebuilt vehicle is a NEW
  asset DIDz carrying a salvage-history credential pointing at the dead
  DIDz. (This mirrors real salvage-title law, and it keeps `destroyed`
  honest.)

## 9. Animals and devices (briefly — customized elsewhere)

- **Animals:** birth → active (custodian!) → deceased. Custody changes are
  the common event (sale of a horse = custody + ownership credential move;
  the animal's DIDz and care history travel like an asset vault). Chip
  replacement = re-anchor ceremony (R5 applies). Fixtures: the four
  existing animals; `petProData`/`equineProData` own the verticals.
- **Devices:** manufacture → active → retired/destroyed. Firmware
  attestation is the device's POL-analog; decommissioning must revoke the
  device's standing grants (a dead sensor must not keep authority).

---

## 10. Cross-cutting cascade table (the hard 20%)

| Trigger | Cascades to | Mechanism |
|---|---|---|
| Human `deceased` | custody, titles, grants issued, wallet contents | LegacyKey succession ceremony + revocation cascade (R1) |
| Org `dissolved` | issuer authority (new issuance only), employees' role credentials, custody of org assets | issuer registry status flip; credentials-already-issued stay verifiable |
| Grantor `suspended` | downstream grants freeze or persist | OPEN (R3) |
| Grant revoked | every delegated child grant, recursively | spec §5.4 (already normative + tested) |
| Asset `destroyed` | all pending transfers, standing disclosures | terminal status; vault becomes read-only archive |
| Custodian change (any tier) | vault access re-keyed; NOT the records | key rotation on the subject's DIDz; provenance appended |

The pattern worth naming: **lifecycle events are authority events.** Every
row above is "a status changed, therefore grants/custody must react." The
kernel's separation of identity (permanent) from authority (revocable) is
what makes each cascade expressible without special-case machinery.

---

## 11. Proposed dossier schema extension (v0.2 candidate)

New OPTIONAL `lifecycle` block on asset dossiers (generated fixtures carry
it now; other categories can adopt it when their fixtures need it):

```jsonc
"lifecycle": {
  "stage": "in-service",         // human-readable stage name (table in §8)
  "story": "…",                   // plain-English situation summary
  "kernelExpectations": ["…"]    // behaviors the gate MUST exhibit for this
                                  // fixture — these become test assertions
}
```

Rationale: TestTown dossiers are test vectors; the `kernelExpectations`
array is where a fixture DECLARES what it is for, so a conformance runner
can iterate the population and know what to assert. Same philosophy as the
villains' `fraudMechanism` — the fixture names its own lesson.

---

*Open rulings R1–R6 await John. Nothing in this catalog changes kernel
semantics; where the spec already rules, this document cites it, and where
it does not, the question is flagged instead of answered.*
