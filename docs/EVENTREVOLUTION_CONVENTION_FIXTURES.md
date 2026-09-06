# Fictional convention district

Added September 6, 2026 for EventRevolution DemoLand. All records carry `MOCK` evidence and are fictional. No real attendees, companies, locations, device serials, or label codes are included. The original TestTown population, authority registries, generator, and adversarial fixtures are unchanged.

The reusable [convention projection](../projections/eventrevolution/convention-v1.json) contains 12 citizen profiles: three enthusiasts, three developers, three founders, and three workers. It includes three fictional crypto companies, one fictional food vendor, four kiosks, three alternate venue identities, six advertising-tag twins, three Arduino receiver twins, and six temporary equipment assignments.

The venues are `studio-hall`, a single-level main hall with peripheral meeting rooms; `split-level`, two principal floors and a halfway VIP (Very Important Person) lounge; and `three-building-campus`, a main building and two satellites connected by outdoor walkways. These are alternative rehearsal layouts. This dataset supplies identities and descriptions, while the consuming application supplies coordinates, floors, paths, accessibility routes, and visibility rules.

Each citizen has a role, biography, interests, optional company affiliation, consent flags, and a simulated availability state. Paused and non-location-sharing examples ensure that a visible directory is not mistaken for permission to display every location. `presenceSlot` is only a named scenario destination, not measured presence. People participate across all three layouts through `venueIds`; they are not simultaneously located in three venues.

The four kiosks use the destination slots `privacy`, `mingle`, `future`, and `food`. Each names its company, eligible venues, and associated workers. Staff are citizen profiles. A kiosk asset never owns its workers, and borrowing a tag does not transfer a person's identity or the device's title.

## Dossiers and evidence

New records follow `testtown/dossier/v0.1` under `dossiers/citizens/`, `dossiers/organizations/`, and `dossiers/assets/`. Every new dossier includes a fictional evidence document and its SHA (Secure Hash Algorithm)-256 digest. The [convention participation registry](../registries/convention-participation-registry.json) confirms participation and synthetic inventory only.

Convention organizations are participant-only dossiers with `identifiers.conventionRegistration` and `participation.issuerAdmission: 'not-requested'`. They are not issuer-admission applications: no government incorporation, tax identifier, license, public key, or trusted-issuer privilege is invented for them. Consumers that need issuer admission must use the existing admission schema and government-registry checks separately.

Equipment adds `ownerOrganizationSlug` where a fictional company owns a kiosk or device. This is a convention-specific extension of the existing asset spine. It is an asserted fixture relationship, not an executed ownership proof. Each identity anchor begins with `TT-CONV-` and is clearly invented. The three venue dossiers use the existing `real-estate` asset kind; the people remain citizens.

## RWAz boundary

RWAz can supply the permanent object-identity, title, encumbrance, and provenance boundary through the shared `ObjectProvider`. The convention projection only describes fixtures. It does not register objects, mint credentials, execute transfers, authorize radio collection, or certify a real device.

An asset identifier, a radio advertisement, a credential, an event assignment, and an individual measurement are different records. Keep EventRevolution's asset catalog, tag adapter, Arduino diagnostic bridge, positioning, and consent logic separate, joining them through explicit references. A purchased device can later have a private inventory record, with a fictional twin retained here. Real labels and person-device assignments do not belong in this public-paper fixture dataset.

QR (Quick Response) codes can help operators look up equipment, but copied codes do not prove device possession, ownership, authenticated firmware, physical proximity, or permission to vote. The BC021 twins support advertising and require an external receiver; they do not scan one another or measure exact distance. Arduino twins represent a scanning capability, but their legacy diagnostic timestamps remain unknown. A registry entry cannot convert retained signal strength into a fresh location fix or a consensus vote.

Two permanent adversarial assets were added: a tag with a copied label and cloned advertisement, and a receiver whose retained signal is presented as fresh proof. They are deliberately excluded from the normal event projection and from the participation registry's authentic inventory. Their `kernelExpectations` state scenarios to exercise; the included tests check fixture integrity and exclusion, not a production anti-cloning mechanism.

## Reproducibility and consumption

```bash
python3 tools/generate_convention_projection.py --check
python3 -m unittest discover -s tests -p 'test_convention_projection.py' -v
```

The dedicated generator creates missing files, leaves matching files untouched, and refuses to overwrite differing content. It does not invoke or modify `tools/generate_population.py`. To evolve this dataset later, preserve prior content and deliberately version the projection and schema rather than using the generator to overwrite history.

EventRevolution should copy and validate the projection at a reviewed TestTown commit, recording the source commit and a digest alongside that copy. The source projection does not embed its own future commit hash. Consumers import TestTown data; TestTown never imports DIDz or EventRevolution code. No live service or runtime dependency on a sibling checkout is implied.

The recovery branch `recovery/pre-eventrevolution-fixtures-2026-09-06` preserves the pre-addition revision `4b25192daa95b7c0e41b9c9e537beee5d445480b`.
