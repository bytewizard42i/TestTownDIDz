# The Secrets Convention

> How TestTown handles keys and seeds, why, and what to copy if you run
> your own test population. This document exists because test projects get
> this wrong more often than they get it right, and the mistake is silent
> until it is expensive.

## The rule in one sentence

**Public halves in the repo, secrets in a local-only vault, backups in a
private place — and no secret ever touches git, not even a worthless one.**

## What that looks like here

TestTown citizens act in the world through wallets. Each wallet produces
three kinds of artifact, and each kind has exactly one home:

| Artifact | Example | Lives in | In git? |
|---|---|---|---|
| **Public card** — address, purpose, funded status | `wallet-bonnie-lachance.md` | the operators' vault folder, referenced from the dossier | yes, harmless |
| **Dossier pointer** — where the card is | `operator.walletCard` in `dossier.json` | this repo | yes, harmless |
| **Seed** — the secret everything derives from | `<slug>.seed` | a local-only folder outside every repo | **never** |

The citizen's dossier carries the `operator` block with the card's path and
the public address. Anyone reading the repo can see *that* a citizen has a
wallet and *what its address is* — both are needed for the fixtures to be
useful. Nobody reading the repo can reconstruct the wallet, because the seed
is not here.

Backups exist: seeds are also copied to a private shared location so a
dead laptop does not strand funded identities. The location is deliberately
not named in public documentation — not because secrecy is the defense, but
because naming it would teach the reader nothing.

## Why not just commit test seeds? They are worthless.

This comes up every time, and the answer has four parts.

**1. Git is forever.** A committed secret is in the history even after you
delete the file. "It's only a testnet seed" is true today; the commit does
not care when things change.

**2. Burned identities cost real time.** Test tokens are free, but faucet
rate limits are not. A leaked seed means anyone can drain or impersonate the
identity, and everything anchored to it — registrations, attestations,
transaction history the fixtures depend on — is compromised with it.

**3. Fixtures teach.** TestTown is standards-bearing material. People copy
the patterns they find here. If the pattern were "seeds in the repo, it's
fine", that pattern would show up in somebody's mainnet project, where the
same mistake is not a faucet problem but a loss of funds.

**4. The convenient path and the correct path are almost the same path.**
One local file per wallet is barely less convenient than one committed file.
The cost of doing it right is near zero, which removes the excuse.

## What the defense actually is

Worth saying plainly: the defense is **never committing the secret**. It is
not secrecy about the pattern. This document tells the world exactly how the
seeds are stored, and that costs nothing, because knowing the pattern gives
an attacker nothing they can use — the seeds themselves are behind the
machine's own security and the private backup's access controls.

Obscurity is not a security boundary. Never committing is.

## Copying this pattern

If you run your own test population:

1. Make a folder outside every git repo. One small file per secret, named
   after what it unlocks. Lock the permissions down (`chmod 700` the folder,
   `chmod 600` the files).
2. Put a backup in one private place you control. Assume the laptop dies
   tomorrow; if that loses a funded identity, your backup is wrong.
3. In the public repo, commit only the public half: addresses, purposes,
   and pointers that say *where* things live without containing them.
4. Write your rule down where contributors will see it. Rules that only
   exist in the maintainer's head get broken by helpful people.
5. When you move to mainnet, change nothing about the shape — only the
   vault gets more serious (hardware keys, stricter backup). The pattern
   already fits.

## The one-sentence version for contributors

If you are about to commit a file and you are not sure whether it is a
secret: it is a secret.
