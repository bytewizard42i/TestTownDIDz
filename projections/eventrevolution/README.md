# Convention projection, version 1

[convention-v1.json](./convention-v1.json) is the reusable fictional event dataset. Its schema identifier is `testtown/eventrevolution-convention/v1`; `eventId` is `demo-convention-2026`. `evidence` is always `MOCK` and `fictional` is always `true`.

| Array | Record contract |
|---|---|
| `venues` | `id`, `name`, `description`, `layoutKind`; no coordinate geometry |
| `people` | `id`, `dossierSlug`, `displayName`, `role`, `biography`, optional `companyId`, `interests`, `consent`, `availability`, optional `presenceSlot`, `venueIds` |
| `organizations` | `id`, `dossierSlug`, `name`, `kind`, `description`, `interests` |
| `kiosks` | `id`, `dossierSlug`, `name`, `companyId`, `kind`, `destinationSlot`, `venueIds`, `workerIds`, `description` |
| `deviceTwins` | `id`, `dossierSlug`, `name`, `kind`, `model`, `role`, `venueIds`, `inventoryIdentifier`, `evidence`, `capabilities`; Arduino records also preserve unknown measurement timing |
| `assignments` | `id`, `eventId`, `deviceId`, exactly one of `profileId` or `kioskId`, `kind`, `evidence` |

Person roles are `enthusiast`, `developer`, `founder`, and `worker`. Availability is `open-to-meet`, `busy`, `unavailable`, or `unknown`. The five consent booleans are `discoverable`, `matching`, `locationSharing`, `availabilitySharing`, and `paused`. A paused profile denies all four sharing/discovery flags. Profiles that do not share location have no `presenceSlot`. Profiles that withhold availability expose `unknown`, except paused profiles explicitly marked unavailable.

The destination and presence slots are `privacy`, `mingle`, `future`, and `food`. The venue adapter resolves these slots to its own checkpoints. Venue IDs (identifiers) are `studio-hall`, `split-level`, and `three-building-campus`. Each is an alternate layout for the same fictional event; this is not live cross-venue tracking.

All foreign references must resolve before consumption. Check `companyId` against `organizations`, `workerIds` and `profileId` against `people`, `kioskId` against `kiosks`, and `deviceId` against `deviceTwins`. Validate evidence labels, consent, supported enums, and venue membership. Human profiles remain separate from equipment assets.

Use a pinned, validated copy in consuming applications with source commit and digest recorded separately. Do not add an undeclared live service or assume this file proves a physical device's identity. See the [fixture and RWAz boundary documentation](../../docs/EVENTREVOLUTION_CONVENTION_FIXTURES.md) and the tests in `tests/test_convention_projection.py`.
