# T05 - Tamper Evidence Versus Immutability

- Evidence date: 28 November 2026
- Tested source baseline: `9b195ed`
- Status: PASS for the reporting requirement

LedgerLock's SHA-256 chain detects inconsistencies in the records supplied to the verifier. It does not make records immutable. An actor able to replace all records and the checkpoint or verifier could create a different internally consistent history. The Render process can also lose its in-memory records on restart.

The protected local HMAC checkpoint improves the controlled demonstration but is not independently managed asymmetric key material. Durable Firestore storage, Cloud KMS signing, least-privilege identities and independent logs remain necessary for the planned cloud release.

The Security Assessment Report preserves this boundary and does not describe local or simulated controls as verified cloud operations.
