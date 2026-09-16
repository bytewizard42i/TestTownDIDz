# SnapBooks projection — Clearwater Plumbing & Heating

> **What this is:** a pointer, not a copy. SnapBooks AI
> ([SnapBooksAi_com_app](https://github.com/bytewizard42i/SnapBooksAi_com_app))
> uses TestTown's existing people and places as its example data, so that
> its demos and tests never touch a real contractor's books.

## Who and what SnapBooks borrows

| TestTown dossier | Role in SnapBooks |
| --- | --- |
| `organizations/clearwater-plumbing-heating` | The example **tenant** (`testtown-clearwater` / `clearwater-plumbing-heating`). EIN, PA registration, and founding date are reused verbatim. |
| `citizens/colin-mcbride` | The signed-in **user** (Master Plumber at Clearwater since 2005). |
| `citizens/anya-petrova` + `assets/petrova-lakeside-cottage` | **Customer + job site**: a pre-sale inspection punch list at 9 Millpond Lane, parcel `TT-PARCEL-0221-033`. The story is consistent with the asset dossier — Anya is selling; the inspection report goes to escrow, not to her. |
| `citizens/edgar-morrow` + `assets/morrow-family-farmhouse` | **Customer + job site**: annual oil-boiler service at 44 Quarry Road, parcel `TT-PARCEL-0917-114` — one of the "decades of repair records" the farmhouse dossier describes. |
| `assets/mcbride-work-van` | Referenced only: the 2015 van was totaled in 2025, so Clearwater's trips log to "Van 2 (2025 replacement)". A salvage rebuild would be a new asset, per that dossier. |

## Where the actual fixture lives

`SnapBooksAi_com_app/app/src/fixtures/testtown-clearwater.ts` — one September
week: 2 job threads, 3 mileage trips, 2 receipts (one deliberately faded),
2 notes (one dictated debrief), 1 final invoice, 1 draft invoice never
finalized. Each record cites the dossier slug or parcel ID it came from.
`bun run seed:testtown` posts the week through SnapBooks' real API.

## Contract

- SnapBooks **reads** TestTown; it does not write dossiers. New citizens or
  assets SnapBooks needs get proposed here first, then borrowed.
- Fixture facts must stay consistent with the dossiers (names, addresses,
  parcel IDs, the van's fate). If a dossier changes, the fixture follows.
- Clearwater is `AUTHENTIC`. If SnapBooks ever wants fraud cases (duplicate
  receipts, a forged supplier invoice), they follow TestTown's `VILLAIN--`
  naming and live in `dossiers/`, not in SnapBooks.
