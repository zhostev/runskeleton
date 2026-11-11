# eval/

Evaluation assets for governed runs.

- `dev/` — development / calibration evaluation data. Freely readable.
- `sealed/` — sealed evaluation data. **Read-only** for run code and role
  sessions; opened only by the gate at promotion time. Writes are blocked
  by the `block-sealed-eval-writes` Kiro hook, and any access must be
  recorded in the ledger.
