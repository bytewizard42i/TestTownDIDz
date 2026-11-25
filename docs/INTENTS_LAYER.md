# The Intents Layer

> **Status**: v0.2 candidate, added Nov 24 2026. First consumer: CryptoSure
> (wallet insurance). Schema reference: `DOSSIER_SCHEMA.md`.

## What it is, in one paragraph

A dossier says what **is**: who someone is, what they own, the papers that
prove it. An **intent** says what somebody **wants**: sell the piano, lend the
van, insure this wallet for $500. Intents sit on asset dossiers as an optional
`intents` list. They are the missing half of "the world before the trust
system": before any gate can say yes or no, somebody has to ask.

## The rule that must never bend

**Intents are wants, never outcomes.** An intent never records whether a check
passed, an offer was made, or a policy was bound. Those facts belong to the
gatekeepers (oracles, registries, contracts) and are recorded by them. The
validator rejects any intent carrying keys like `approved` or `kycPassed`.

Why so strict: the moment a fixture says "approved", a consumer can skip its
own check and still look correct. TestTown exists to make gates work for
their living.

## Two levels

| Level | Required | Optional |
|---|---|---|
| **Generic intent** (anything) | `wants`, `expressedAt`, `status` | `startDate`, `expiresAt`, `story`, `category` + its block |
| **Insurance wish** (`category: "insurance"`) | all of the above **plus** `startDate`, `expiresAt`, `insurance.wish`, `insurance.coverageUsd` | `story` |

A category names one extra block holding its details. Unknown categories are
allowed and free-form, which is how a new kind of want gets tried before
anyone writes rules for it.

## Lifecycle

```
expressedAt ──► startDate (when it should take effect)
     │
     └────────► expiresAt (unanswered past this, it is stale)

status:  open ──► accepted   the owner took an offer
           ├────► withdrawn  the owner changed their mind
           └────► expired    nobody answered in time
```

- "Now" for a fixture is the asset's `holdings.asOf`, never the real clock,
  so a fixture means the same thing whenever the tests run.
- `expiresAt` may fall before `startDate` (ask open to Dec 31, cover from
  Jan 1).
- Old intents stay in the dossier as history. A consumer must not treat an
  `expired` or `withdrawn` intent as a live ask.

## Where to look

| You want | Open |
|---|---|
| Copy-paste examples, valid and broken | `examples/intents-examples.json` |
| The rules, with the reasoning in comments | `tools/validate_intents.py` |
| A quick check of everything | `python3 tools/validate_intents.py` |
| Real fixtures | `dossiers/assets/*-wallet/dossier.json` |
| The tests | `tests/test_intents_layer.py` |

## The current cast

Seven citizens each hold a pretend crypto wallet and want it insured. Balances
and wishes are deliberately uneven.

| Citizen | Balance | Wants | Worth noticing |
|---|---:|---:|---|
| Bonnie LaChance | $420 | $500 | small, well matched |
| Mei-Lin Zhao | $8,750 | $10,000 | rounded up on purpose |
| Theo Brandt | $2,300 | $2,500 | a claims adjuster insuring himself |
| Marcus Reid | $4,600 | $5,000 | two intents: one expired in July, one live |
| Raj Patel | $950 | $1,000 | cautious, matched |
| Priscilla Vance | $14,200 | $1,000 | under-insured deliberately; expiry before start |
| Harold Quist | $310 | $1,000 | over-insured three to one |

## How a consumer should read an intent

1. Take only intents whose `status` is `open`.
2. Check `expiresAt` against your own clock. A fixture frozen in November is
   not a promise about February.
3. Honor `startDate`: do not begin before the owner asked.
4. Read the category block for the details.
5. Decide for yourself. Record your decision in **your** system, not here.

## Ideas and open questions

None of these are built. They are here so the thinking is not lost.

**More categories.** `selling`, `lending`, `gifting`, `bequeathing`,
`repairing`, `appraising`, `renting`. Each would add its own block and, when
it has real rules, a checker in `CATEGORY_CHECKERS`.

**More insurance wishes.** `raise-cover`, `lower-cover`, `renew-cover`,
`cancel-cover`, `add-beneficiary`. Most would need to point at an existing
policy, which raises the question of how a want refers to an outcome it does
not own. Probably by an opaque reference the insurer issued.

**Intents on other dossiers.** Today only assets carry intents. A citizen
could want something that is not about one asset ("open a bank account",
"get a passport"); an organization could want to become a trusted issuer.
The generic object already fits; only the placement rule would change.

**Villain intents.** TestTown's villains use the identical schema. A villain
intent would be well formed and still wrong: someone voicing a want over an
asset they do not own, or insuring the same wallet with three insurers at
once. This is the natural fraud test for any consumer.

**Conflicting and chained intents.** Two open intents that cannot both be
met (sell the cottage and insure it for five years). A `supersedes` pointer
from a new intent to the one it replaces, so Marcus's November ask would
visibly follow his expired spring ask.

**Conditional intents.** "Insure the wallet only if the premium is under $10
a month." A `conditions` list in the generic object. Tempting, but it is the
first step toward a negotiation language, so it needs a real use first.

**Offers as the mirror image.** If intents are asks, the answering side has
offers. Offers are NOT TestTown's to hold, but a consumer might want a shared
shape so an intent and an offer can be matched mechanically.

**Privacy.** An insurance wish next to a balance tells the world how much
someone holds. In the real system the want would be private and only a
commitment would be public. A fixture could carry a `disclosure` hint saying
which fields the owner is willing to reveal, and to whom.

**On-chain anchoring.** Hash an intent and record the hash, so an owner can
later prove "I asked for this, on this date, before the price changed"
without revealing what they asked for.

**Currencies and amounts.** `coverageUsd` assumes dollars. A `currency`
field, or an amount expressed as a share of the balance ("cover 100%").

**Time.** A sweeper that marks open intents expired as a simulated clock
advances would let consumers test the transition instead of only its two
ends. Recurring wants ("renew every year") are a related question.

**A generator.** `tools/generate_population.py` builds citizens. A sibling
could give every citizen a plausible set of wants, so a consumer can test
against hundreds of intents instead of eight.

**Coverage versus balance.** The mismatches (Priscilla, Harold) are the
interesting cases for an insurer's education and sizing step. Worth adding a
few more shapes: a balance that changed after the wish was voiced, and a
wish for an amount no policy tier offers.
