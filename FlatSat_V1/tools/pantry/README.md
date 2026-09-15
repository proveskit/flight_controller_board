# tools/pantry — checked-in symbol pantry for the Phase-1 sheet generators

Each `.sexp` file is one flattened `(symbol "Lib:Name" ...)` block, indented two tabs,
ready to paste inside a sheet's `(lib_symbols ...)`.
File name = symbol name with `: / space ( )` replaced by `_`
(`re.sub(r'[:/ ()]', '_', lib_id) + '.sexp'`, the mapping every generator uses).

## Why this directory exists

Review finding 13. The six Phase-1 generators in `tools/gen/` originally read their
lib_symbols blocks from a **session-scoped scratchpad** path
(`/private/tmp/claude-501/.../scratchpad/pantry`). That directory is temporary: once the
capture session is gone, all six generators abort at `open()` and the fix-stage convention
("a regeneration must reproduce the sheet") is unenforceable for anyone else. Nothing else
under the repo held these blocks. This directory is that content, checked in.

## Contents

42 blocks — exactly the set referenced by the `(lib_symbols ...)` of the six Phase-1 sheets
(`emulator_mcu`, `solar_emulation`, `solar_power_injection`,
`battery_protection_replica`, `pyro_inhibit`, `bench_io`).

Copied verbatim from the capture session's scratchpad pantry, except
`Transistor_FET_BSS138.sexp`, which came from `scratchpad/work_bench_io/`
(the only used block that was never in the pantry proper).
`work_bench_io/Switch_SW_SPDT.sexp` was byte-identical to the pantry copy, so there is
only one `Switch_SW_SPDT.sexp` here.

Verified at copy time: after the one documented `LIB_FIXUPS` substitution
(`Driver_Haptic:DRV2605LDGS`: `Package_SO:VSSOP-10_3x3mm_P0.5mm` ->
`Package_SO:TSSOP-10_3x3mm_P0.5mm`), **all 42 blocks are byte-identical to the block the
corresponding delivered sheet embeds**. A generator repointed at this directory therefore
emits the same `lib_symbols` section it emits today.

`INDEX.md` carries the per-symbol provenance table from the capture session (it lists the
94 blocks the session pantry held; the 52 not listed above are simply unused by these six
sheets). Fetch more with
`tools/get_symbol.py "Lib:Name" --sch-dirs <upgraded refs dir>`.

## Contract the generators should use

Intended (finding 13) for all six generators — env-var override, repo-relative default,
no absolute session path:

```python
HERE = os.path.dirname(os.path.abspath(__file__))
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))
```

### Status — DONE (integrator fix round 2, 2026-09-14)

All six generators now use the contract above. No generator contains a
`/private/tmp/.../scratchpad` path any more:

| generator | constant | now |
|---|---|---|
| `emulator_mcu_gen.py` | `PANTRY` | `os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))` |
| `solar_emulation_gen.py` | `PANTRY` | same (env var renamed `PANTRY` → `FLATSAT_PANTRY`) |
| `battery_protection_replica_gen.py` | `PANTRY` | same (env var renamed `PANTRY` → `FLATSAT_PANTRY`) |
| `solar_power_injection_gen.py` | `PANTRY` | same, via `TOOLS` (was hardcoded, no override) |
| `pyro_inhibit_gen.py` | `PANTRY` | same (was `SCRATCH_PANTRY`, hardcoded; the one use site follows) |
| `bench_io_gen.py` | `PANTRY` | same; the separate `WORK` constant is **deleted** — `Transistor_FET:BSS138` now comes from this directory |

Proven, not assumed: the session scratchpad `pantry/` and `work_bench_io/` directories were
renamed away and all six generators re-run — every one succeeded and produced a file
byte-identical to the committed sheet. Plain `python3 tools/gen/<key>_gen.py`, no env var,
is now the supported invocation; `FLATSAT_PANTRY=<dir>` only overrides it.

`solar_emulation_gen.py`'s `LIB_FIXUPS` is also idempotent now: it aborts only when a block
carries *neither* the old nor the new string, so a pantry rebuilt **from** a delivered sheet
(`TSSOP` already substituted) no longer kills the generator. Verified by rebuilding a
post-fixup copy of this directory and regenerating to a byte-identical sheet.

### Related: uuid stability (review fix 14)

All six generators now draw uuids from a **seeded** `random.Random` stream
(`_rng = random.Random('flatsat-<key>-2026-09-14')`,
`uuid.UUID(int=_rng.getrandbits(128), version=4)`), so re-running one reproduces the
committed sheet byte for byte instead of re-keying every item. Set `FLATSAT_FRESH_UUIDS=1`
to get real random uuids — only ever needed when deliberately re-keying a sheet.
(`battery_protection_replica_gen.py` already worked this way and additionally pins its own
file-level `SHEET_FILE_UUID`; the other five take the file uuid from the same seeded stream.)
