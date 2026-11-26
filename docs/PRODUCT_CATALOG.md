# The Product Catalog

> **Status**: v0.2 candidate, added Nov 26 2026. First consumer: CryptoSure
> (wallet insurance). Companion to `INTENTS_LAYER.md`. Schema reference:
> `DOSSIER_SCHEMA.md`.

## What it is, in one paragraph

An intent says what somebody **wants**: "insure this wallet for $500". A
**product** says what a shop **sells**: "wallet theft cover, $100 to $1,000,
$20 a year". Until the catalog existed, TestTown's wishes had nothing to
meet. Products live in `dossiers/products/`, one folder each, and the
organizations that underwrite and sell them carry a `storefront` block
pointing back.

## Product, offer, policy: only the first lives here

Everyday speech calls all three of these "a policy". They are different
things, and the difference decides where each one is allowed to live.

| Thing | What it is | Same for everybody? | Lives in TestTown? |
|---|---|---|---|
| **Product** | A standing catalog entry, like a diner's menu | Yes | **Yes** |
| **Offer** | A shop's answer to one person's ask | No | No, the seller's own system |
| **Policy** | One person bound to one set of terms | No | No, the seller's own system |

An offer and a policy are **outcomes**: somebody ran checks and decided. The
intents layer has a rule that must never bend, "wants, never outcomes", and
the catalog obeys the same rule from the other side:

**A product may say what it requires. It may never say who passed, and it
may never name a customer.**

The validator rejects any product carrying keys such as `approved`,
`customers` or `issuedTo`, anywhere inside it.

## Who is who

| Role | Meaning | In TestTown |
|---|---|---|
| **Underwriter** | Carries the risk | Ironclad Insurance Group, the town insurer since 1961 |
| **Seller** | Puts the product on a shelf | Quarry Street Exchange sells wallet cover; Ironclad also sells direct |

One organization can be both. A product names its underwriter and sellers by
slug, and each of those organizations lists the product in its `storefront`.
The link runs both ways on purpose, so a one-sided claim stands out.

## The shape

```jsonc
{
  "schema": "testtown/dossier/v0.1",
  "category": "product",
  "slug": "wallet-theft-cover-starter",
  "displayName": "Wallet Theft Cover, Starter",
  "honesty": { "role": "AUTHENTIC", "fraudMechanism": null },

  "productKind": "insurance",              // names the details block below
  "underwriterOrganizationSlug": "ironclad-insurance-group",
  "sellerOrganizationSlugs": ["quarry-street-exchange", "ironclad-insurance-group"],

  "availability": {
    "status": "on-sale",                   // announced | on-sale | withdrawn
    "listedAt": "2026-10-01",              // when it went (or will go) on the shelf
    "withdrawnAt": "…",                    // only when status is withdrawn
    "asOf": "2026-11-25"                   // the fixture's frozen "today"
  },

  "insurance": {
    "covers": { "dossierCategory": "asset", "kinds": ["crypto-wallet"] },
    "peril": "unauthorized transfer out of the insured wallet",
    "coverageUsd": { "min": 100, "max": 1000 },   // a range, not one amount
    "deductibleUsd": 50,                   // what the customer bears first
    "premiumUsdPerYear": 20,
    "termMonths": 12,
    "requires": ["screening-check", "region-check", "identity-check"]
                                           // NAMES of checks, never results
  },

  "evidence": "MOCK", "fictional": true,
  "documents": [ { "file": "product-sheet.md", "sha256": "…" } ]
}
```

**Generic first, specific second**, exactly like intents. `productKind` names
one block holding that kind's details. An unknown kind is allowed and its
block is free-form. `insurance` is the first kind with rules of its own.

## What is on the shelf today

Every number is a round, invented placeholder. None of it is anybody's real
pricing.

| Product | Covers | Amount | Status | Worth noticing |
|---|---|---:|---|---|
| Wallet Theft Cover, Starter | crypto wallet | $100 to $1,000 | on sale | fewest checks |
| Wallet Theft Cover, Standard | crypto wallet | $1,001 to $5,000 | on sale | all five checks |
| Wallet Theft Cover, Plus | crypto wallet | $5,001 to $25,000 | on sale | has a minimum |
| Equine Mortality Cover | horse | $1,000 to $50,000 | on sale | an animal, not an asset |
| Wallet Theft Cover, Launch Special | crypto wallet | $100 to $2,000 | **withdrawn** | history; must not be sold |
| Vehicle Theft Cover | vehicle | $2,000 to $60,000 | **announced** | not for sale until Jan 15 2027 |
| VILLAIN: Guaranteed Wallet Cover | crypto wallet | $100 to $100,000 | on sale | fraud, see below |

The three wallet sizes touch but never overlap, so any amount from $100 to
$25,000 fits exactly one of them.

## The wish meets the shelf

`tools/validate_catalog.py` has a small matcher, `products_that_fit(wish,
subject, products)`. Given an insurance wish and the dossier it is about, it
returns the products that are on sale, cover that kind of thing, and include
the amount asked for.

**It is a lookup, not a decision.** "Fits" means the shelf label matches the
ask. It says nothing about whether the owner would pass any check.

The same matcher serves a wallet and a horse. That is the point of keeping
the catalog generic: one matcher, many stores.

### Naming a product (optional)

An insurance wish may carry `insurance.productSlug` to say exactly which
product the owner wants. Leaving it out is just as valid; most of the town
is product-blind.

| Citizen | Asks for | Names | Result |
|---|---:|---|---|
| Mei-Lin Zhao | $10,000 | Plus | fits. She ran her own numbers |
| Harold Quist | $1,000 | Plus | **does not fit**: below Plus's $5,001 minimum. He wanted "the good one" |
| the other five | various | nothing | the matcher finds one product each |

Harold's mismatch is deliberate. The fixture is correct; the *ask* is wrong,
because people really do ask for the wrong product. A consumer has to cope:
suggest Starter, explain the minimum, or decline.

A wish naming a product that does not exist is different: that is a broken
fixture, and the tests fail on it.

## The villain

`VILLAIN--guaranteed-wallet-cover--names-an-underwriter-that-never-agreed`
uses the identical schema and passes every shape rule. A hundred thousand
dollars of cover, five dollars a year, no checks.

The fraud is a claim the world cannot back: it names Ironclad as its
underwriter, and **Ironclad's storefront does not list it**. A consumer that
only checks shape will sell it. A consumer that follows the link back to the
underwriter will not. Its seller is also a villain, the organization whose
EIN the IRS registry never issued.

## How a consumer should read a product

1. Take only products whose `availability.status` is `on-sale`.
2. Check `listedAt` against your own clock, as with an intent's dates.
3. **Follow the link back.** Confirm the underwriter's `storefront` lists
   the product. This is what catches the villain.
4. Confirm the underwriter and seller are themselves in good standing in the
   registries.
5. Read the kind's block for the terms.
6. Run the `requires` checks yourself. Record the results in **your**
   system, never here.

## Real terms belong in a private overlay

The shape is public; real numbers need not be. A consumer with real product
terms keeps them in its own private repo as product dossiers in this same
shape, and checks them with these same functions:

```python
from validate_catalog import load_products, all_product_problems
private_products = load_products(folder="<your private products folder>")
```

A private product cannot be listed in a public organization's storefront, so
an overlay checks shape and skips the backlink.

## Where to look

| You want | Open |
|---|---|
| Copy-paste examples, valid and broken | `examples/catalog-examples.json` |
| The rules and the matcher, with reasoning in comments | `tools/validate_catalog.py` |
| A quick check of everything | `python3 tools/validate_catalog.py` |
| The products table (edit here, then regenerate) | `tools/generate_population.py` |
| The products themselves | `dossiers/products/*/dossier.json` |
| The tests | `tests/test_product_catalog.py` |

Products are **generated**. To change one, edit the `PRODUCTS` table in
`tools/generate_population.py` and run it. The dossiers, the product sheets,
their hashes and the storefronts are all rewritten together, so they cannot
drift apart.

## Ideas and open questions

None of these are built. They are here so the thinking is not lost.

**A licence registry.** A mock State Insurance Department would give "is
this underwriter allowed to sell insurance?" an authority of record, the way
the IRS registry answers "was this EIN issued?". A second villain could then
be an unlicensed underwriter with honest paperwork.

**Non-insurance products.** A loan, a custody plan, a vet wellness plan, a
school course. The generic product already fits; each needs only its own
details block and, when it has real rules, a checker.

**Cover on a person.** Health and life cover would make `citizen` a
coverable category. Left out until a fixture needs it, because it raises
privacy questions that cover on a watch does not.

**Pricing that is not flat.** A rate ("1.8% of the amount"), a table by
amount, or a price that depends on which checks the buyer cleared.

**Bundles, riders and prerequisites.** "Wallet cover plus a hardware wallet
discount", or a product that can only be bought with another.

**Regional availability.** "Not sold outside the county" would let the
matcher use a region, and would exercise a region check end to end.

**Intents on animals and citizens.** Today only assets carry intents, so
the horse is matched in tests with a hand-made wish. Letting an animal
dossier carry intents would give Ember a real one.

**A seeded mixer.** Draw a person, an asset, a wish and a product from
separate pools by a seed number, under plausibility rules, to test rules
across thousands of combinations. The hand-written cases stay as the canon;
the mixer adds volume. A seed makes every failure replayable.

**Products as the other half of an on-chain match.** Hash a product sheet
and anchor it, so a seller can later prove "these were the terms on the
shelf that day" without a trusted archive.
