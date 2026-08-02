# TestTown Threat Model v0.1 — the Fraudulent Issuer

> **John's ruling (Aug 2, 2026):** "The worst-case scenario for the DIDzM
> ecosystem would be for an entity to be accepted as a trusted issuer that
> is not authentic — this would create a duplicate, and a vector for
> massive fraud."

## Why issuer admission is the crown jewel

A compromised HOLDER loses one identity. A compromised VERIFIER makes one
bad decision. A fraudulent ISSUER mints **unlimited credentials that
verify perfectly** — every downstream proof is cryptographically sound and
semantically poisoned. The cryptography cannot save you here: the fraud
happened at admission, before the first proof was ever generated.

## Attack classes TestTown embodies (as permanent villain residents)

| # | Attack | Resident villain | The tell the gate must catch |
|---|---|---|---|
| 1 | Fabricated identity | `VILLAIN--shady-docs-llc--forged-ein-not-in-irs-registry` | EIN well-formed, absent from the IRS registry |
| 2 | Zombie impersonation | `VILLAIN--first-dmv-of-delaware--impersonates-dissolved-entity` | Registration exists but standing = DISSOLVED, officers mismatch |
| 3 | Authority inflation | `VILLAIN--evergreen-diploma-mill--accreditation-cites-nonexistent-board` | License cites an accreditor absent from every registry |
| (roadmap) | Scope creep | an admitted mechanic attesting BIRTH_CERTIFICATE | scope enforcement post-admission |
| (roadmap) | Key theft | operator key rotation drill | recovery + revocation ceremonies |

## The defense the gate must implement (and TestTown makes testable)

1. **Independent confirmation, never self-attestation**: every dossier
   claim is cross-checked against the authorities of record
   (`registries/`). Beautiful paperwork is not evidence; confirmation is.
2. **Assurance-level ceilings**: admission maps issuer type → maximum
   TrustedIssuerRegistry assurance level (a mechanic can never be
   SYSTEM_CRITICAL).
3. **Scope minimalism**: attestation scopes granted = the intersection of
   requested scopes and what the confirmed licenses support.
4. **Auditability**: every admission decision records WHICH confirmations
   were performed — the review itself leaves a dossier.

## The acceptance test that must never be deleted

> For every `VILLAIN--*` dossier: the admission ceremony REFUSES it, with
> a reason naming the exact failed confirmation.
> For every authentic organization: the ceremony ADMITS it at the correct
> assurance level with the correct scopes.

Removing a villain from TestTown weakens the gate's regression suite —
villains are protected residents.
