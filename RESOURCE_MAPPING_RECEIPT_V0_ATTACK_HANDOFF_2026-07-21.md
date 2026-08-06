# Resource Mapping Receipt v0 — Bounded Attack Handoff

Date: 2026-07-21
Status: LOCAL CANDIDATE — attack before push
Remote floor: `origin/main == 9c6a967`
Candidate HEAD: `0899306`

## Candidate chain

| Commit | Role |
|---|---|
| `7b279a9` | Freeze Resource Mapping Receipt v0 law |
| `323de27` | Freeze 14-case adversarial packet |
| `7f1ccba` | Correct RM-13 census reachability |
| `3292c98` | Implement PASS A |
| `f72ca24` | Harden receipt coherence and close Anchor AC-2 |
| `51ca725` | Separate active mappings from stale historical receipts |
| `0899306` | Lock subject-time boundaries and mixed-candidate regressions |

Do not push, edit the candidate, open a connector, or write an article during the attack.

## Fingerprints

```text
85940597e3f144a9e6d80226a91cae6c09e0af89b9c6dcb28e7aa0a9c7f52728  PATH_A_V3_PREREGISTRATION_RESOURCE_MAPPING_RECEIPT_V0_2026-07-21.md
9a181a728833bddf2b64077a67307c2675bda932d667cde72f637b4418d9262f  tests/fixtures/path_a_v3_resource_mapping_receipt_v0_2026_07_21.json
a170d9c5c797d0df26e64a4e2ef940a749ad90f34006d3c7f0a3cd1f59a15edc  agents/resource_mapping.py
192b42d41184d83c3dcac2bff54af226f58b4712d36caffca24a8b3397106922  agents/anchor_contract.py
a3c752e95b00ea744b38ade18ca8259bd0c288dda0db0d27c514c96b7109e43b  tests/test_resource_mapping.py
cd0c5995c70d5fb10d2989c3ef6aaf6392befe3def1347005a14fe757cd328f0  RESOURCE_MAPPING_RECEIPT_V0_PASS_A_RESULT_2026-07-21.md
f95c14a4e1dcab8cec6485901ba673bdcaf28ede86de629109e6acf919df1555  path_a_eval_artifacts/path_a_v3_resource_mapping_receipt_v0_pass_a_20260722T014028Z.json
```

## Known freeze correction

The first implementation run found RM-13 could not reach its intended alias-cycle boundary because it requested canonical namespace `github` while reusing the `tenant.demo` census. Commit `7f1ccba` gives RM-13 an integrity-valid `github/compliance.export_approval` census. Expected alarm remains `mapping_target_not_canonical`; resolver order and law did not change.

Attack whether this is a legitimate reachability correction. Block if it weakens any pre-registered bar or hides a prior implementation failure.

## Required attack matrix

1. Independently recompute the base canonical assertion and mapping key. Expected:

   ```text
   mapping:v0:sha256:760b5c43822b288e1ada1f9425a7842ae52079ae9d0d5288baddf832590b83ef
   ```

2. Recompute every embedded policy, grant, assertion, mapping-receipt, revocation, and census digest. Do not inherit the result report.
3. Run all 14 frozen cases and verify every expected field, not only `alarm_code`.
4. Mutate each of the seven semantic assertion fields independently; every mutation must change the mapping key. Provenance-only decorations must not.
5. Attack assertion and receipt typing: empty IDs, non-string IDs, extra semantic-looking fields, naive timestamps, floats, and malformed evidence lists.
6. Attack authority: issuer/grantee mismatch, recomputed costume grantor, wrong namespace, wrong kind, wrong scope, expired grant at issuance, revoked grant at issuance, receipt outliving grant, duplicate/conflicting grant IDs.
7. Attack the two clocks at equality boundaries: issued/effective exactly at subject time, expiry exactly at subject time, revocation exactly at resolution time, revocation one tick after resolution, and resolution before subject/observation.
8. Attack active-set behavior:
   - valid + expired;
   - valid + revoked;
   - valid + future;
   - two valid same-target receipts;
   - two active different-target receipts;
   - valid + unauthorized costume.
   Stale/inactive receipts must remain diagnostic without vetoing a separate valid active mapping. Conflicting active targets must block.
9. Attack replay identity: identical receipt replay collapses; same receipt ID with different valid canonical bytes fails before target choice.
10. Attack revocation isolation: an unrelated malformed revocation must not poison the candidate; a matching malformed or unauthorized revocation must fail loud.
11. Attack census binding: altered digest, duplicate IDs, wrong namespace/scope, future observation, absent canonical target, and target present only as an alias.
12. Attack direction and chain boundaries: reverse lookup, same-namespace alias chain, two-node cycle, and a longer transitive chain. V0 must never recurse.
13. Attack the Anchor bridge with:
    - arbitrary truthy JSON;
    - altered source identity;
    - altered authority scope;
    - altered subject/resolution clocks;
    - altered census receipt ID;
    - recomputed mapping key for a census-absent target;
    - a valid RM-1 resolution bound to the Anchor AC-2 census.
    Only the final valid receipt may close AC-2, and its surface key must equal AC-1 exactly.
14. Confirm failure paths never expose `mapping_key` or `canonical_resource_id`, including mixed-candidate and bridge failures.
15. Run focused and full suites. Current maker receipt: 20 Resource Mapping tests; 33 combined Resource Mapping + Anchor Contract tests; 80 passed / 1 expected xfail full.

## Claims to grade

- A mapping is directional, exact-scope, and authority-grant bound.
- Mapping validity is evaluated at subject time; revocation admissibility is evaluated at resolution time.
- Only active conflicting targets block; inactive history stays visible but does not veto a valid mapping.
- The canonical target must already exist in the bound census.
- The mapping key identifies semantics; receipt/grant/time provenance decides admissibility.
- A coherent mapping resolution can close Anchor AC-2 without sharing a fixture surface ID.
- The bridge is coherence validation, not cryptographic authentication.

## Non-claims

- No automatic mapping discovery.
- No signatures, verified key ownership, transparency log, or cryptographic independence.
- No symmetric or transitive identity.
- No connector, real external replay, deployment, relation-store mutation, or public article.

Return one of: `PASS`, `BLOCKING`, or `PASS WITH NON-BLOCKING NOTES`. Identify the exact candidate fingerprint for every blocker. Do not edit the candidate.
