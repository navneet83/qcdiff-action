# qcdiff-action

GitHub Action that fails a job when an OpenQASM 3 circuit drifts from its checked-in reference. It runs [qcdiff](https://github.com/navneet83/qcdiff), a semantic gate-level diff, so comment, whitespace, and declaration-order changes do not trip the gate; real changes show up as added, removed, or re-parameterized gates in the log and in the job step summary.

## Usage

```yaml
# Fail when the transpiled circuit drifts from the reference
# (e.g. after a qiskit upgrade).
- uses: navneet83/qcdiff-action@v1
  with:
    old: reference/ghz.qasm
    new: build/ghz.qasm
```

Inputs: `old` and `new` are the two circuit files; `quiet: "true"` limits output to the summary counters. The step exits 1 on drift and 2 on parse errors, and sets a `changed` output (`"true"`/`"false"`) for later steps that want to react without failing the job:

```yaml
- uses: navneet83/qcdiff-action@v1
  id: drift
  continue-on-error: true
  with:
    old: reference/ghz.qasm
    new: build/ghz.qasm
- if: steps.drift.outputs.changed == 'true'
  run: echo "circuit changed, regenerate the reference if intentional"
```

The action installs the [qcdiff wheel from PyPI](https://pypi.org/project/qcdiff) (a few seconds; linux, macOS, and Windows runners all have prebuilt wheels).

`qcdiff` reports what changed, not whether the circuits are equivalent; for formal equivalence checking use [mqt-qcec](https://github.com/munich-quantum-toolkit/qcec).

## License

Apache-2.0
