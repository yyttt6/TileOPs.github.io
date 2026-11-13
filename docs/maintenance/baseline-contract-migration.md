# v0.1.0 baseline metadata joins

A successful measurement and a successful website deployment do not prove that
its TileOPs timing was joined to the baseline table. Run 43275057419 measured
174 operators / 1809 cases, while 605 cases did not match saved baseline keys.
The saved rows and latencies remain authoritative.

The explicit mapping in `scripts/baseline_contracts.py` covers public spelling
changes, tensor/scalar argument renames and the documented `validate_inputs=False`
default. True stays distinct. Engram's legacy redundant dimensions are removed
only if they agree with tensor shapes. INT8's old per-block name refers to the
same 1x128 row groups now called per-token/group; it is not FP8's 128x128 layout.
Every remaining shape, dtype, axis, scale, numerical mode and other scalar stays
part of the comparison key. Conflicting old/new argument names are rejected.

Sources: the frozen measured TileOPs commit
`eab4b9cd12953651e75cd1bb3741b4b850e2ff42`, its `src/tileops/_ops`,
`workloads` and `benchmarks` definitions, and the saved baseline workload metadata.
`tests/fixtures/v010_metadata_alias_cases.json` retains one old/current contract
pair for each of the 44 affected operators. The full replay resolved all 605
joins; 8327 altered tensor shapes were rejected and 2414 boolean changes remained
distinct. No measurement, latency, baseline ID or timing protocol was changed.

Snapshot identity `v010-reviewed-aliases-v1` continues to replay through the frozen
`baseline_contracts_v1.py`; new snapshots use v2. Do not change the v1 mapper when
adding mappings. Old sealed bundles must still validate byte-for-byte. Rendering
can rejoin their saved verified measurements using the current mapper without
rerunning NPU measurements. Among equivalent saved timings, use the newest
measurement date, and reject conflicting timings at the same date.

Only validated metadata with `status=passed` and `selection_scope=all` may mark a
full nightly as current. An older partial run remains on its historical page;
its failures must not annotate the latest successful operator tables. A newer
partial run still exposes its failures.

## TopKSelect follow-up (PR81)

Three previously unregistered TopKSelect cases use `logits`, `indices`, and
`top_k` where the saved baseline records use `index_score`, `indexes`, and
`topk`. The input, per-row start/end bounds, output [B,S,G,K] layout and dtypes
are unchanged. The v3 mapping adds only these explicit argument aliases.
`baseline_contracts_v2.py` preserves the complete previous mapper for sealed v2
snapshot replay; new snapshots declare v3. Existing PR measurements can be
compared offline without restarting their device jobs.
