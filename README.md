# CortexLedger

A public GenLayer fact-verification ledger for Technology and Science claims.
Each submission is checked by a GenLayer Intelligent Contract that fetches live web
evidence, asks validators to judge the claim from that evidence, and stores only
approved facts on chain.

- Live app: https://cortex-ledger.vercel.app
- Network: GenLayer Bradbury Testnet
- Contract: 0x1Ef7A3c0641EB62c32d1CA022a6F84a874Ce8c96
- Explorer transaction: https://explorer-bradbury.genlayer.com/tx/0xa1aebb54f838f2bd83670fd9c5a0f85ec2bd252845099738687ac884b7dfb456

## What changed after review

The first version depended mainly on an LLM prompt. This update changes the core
architecture so the contract no longer relies on the model's limited training data.
For every submission, the contract performs live web fetching through GenLayer
non-deterministic execution and validates the result through the Equivalence
Principle lifecycle.

## What it does

1. `submit_fact(category, title, content)` receives a Technology or Science claim.
2. The contract checks deterministic rules first:
   - English-only content
   - no politics
   - category must be `Technology` or `Science`
   - content must contain at least two specific sentences
3. Validators fetch live web evidence from Wikipedia search using
   `gl.nondet.web.get`.
4. The LLM receives the submitted claim plus the fetched evidence and must decide
   from the evidence only.
5. A validator function re-fetches the same evidence and verifies that the leader's
   proposed verdict is structurally valid and based on the same source set.
6. If approved, the fact is stored in `verified_ledger` with the author, category,
   title, content, reasoning, and first source URL.

## Why this uses GenLayer properly

- The contract inherits from `gl.Contract`.
- On-chain state is declared as typed class-level storage.
- Web fetching happens inside an inner non-deterministic function.
- Consensus is handled with `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)`.
- The contract does not simulate validators with a manual loop.
- The LLM is not used as a standalone oracle; it receives current web evidence
  fetched during validator execution.

## Smart contract

Source: [`contracts/review.py`](contracts/review.py)

Main public methods:

- `submit_fact(category, title, content)` — verifies a claim and stores it only if
  approved.
- `get_verified_ledger()` — returns all approved ledger entries.
- `get_last_verdict()` — returns the latest verification decision, including
  reasoning and web evidence metadata.

## Example lifecycle to include after deploy

After deploying the updated contract on Bradbury, submit a clear Technology or
Science fact, then add the transaction here:

- Contract: `0x1Ef7A3c0641EB62c32d1CA022a6F84a874Ce8c96`
- Successful verification transaction: `0xa1aebb54f838f2bd83670fd9c5a0f85ec2bd252845099738687ac884b7dfb456`
- Explorer: `https://explorer-bradbury.genlayer.com/tx/0xa1aebb54f838f2bd83670fd9c5a0f85ec2bd252845099738687ac884b7dfb456`

## Project structure

```text
cortex-ledger/
├── contracts/
│   └── review.py
├── public/
│   ├── index.html
│   ├── leaderboard.html
│   └── submit.html
├── package.json
├── vite.config.js
└── README.md
```

## Local development

```bash
npm install
npm run dev
```

Before publishing the frontend, replace the placeholder contract address in:

- `public/index.html`
- `public/submit.html`

with the newly deployed Bradbury contract address.


