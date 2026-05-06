# sfmapi benchmarks

This directory tracks reconstruction quality + wall-clock cost over
time. The harness drives a running sfmapi server through the SDK,
runs a small set of reference datasets through the incremental
pipeline, captures metrics from the resulting reconstruction, and
appends them to a JSONL time-series under `results/`.

## Layout

```
bench/
  datasets/                # dataset specs (YAML, no images)
    fountain.yaml
    panther.yaml           # add your own under here
  harness.py               # drives the SDK, captures metrics
  metrics.py               # quality + cost extraction
  store.py                 # results JSONL append + load + lint
  cli.py                   # `python -m bench.cli {run, lint, plot}`
  results/
    <git-sha>.jsonl        # one JSON line per (dataset, recipe, run)
```

## Run

A live sfmapi server (and its worker, with pycolmap available) must be
reachable. Each dataset spec points at images via either an
`image_root` (local path the worker can see) or an `s3` source.

```bash
# One-off
python -m bench.cli run --dataset fountain \
    --base-url http://localhost:8080 \
    --api-key sfm_...

# All datasets
python -m bench.cli run --all

# Lint the latest results against history (regression gate)
python -m bench.cli lint --tolerance 0.05
```

The lint command compares the latest run for each (dataset, recipe)
against the rolling median of the previous N=10 runs and exits
non-zero if any of these regress beyond `--tolerance` (default 5%):

| Metric | Direction |
|---|---|
| `num_reg_images` | higher is better |
| `num_points3D` | higher is better |
| `mean_reproj_err` | lower is better |
| `wall_seconds` | lower is better (informational; default tolerance 25%) |

## CI integration

Run nightly on the GPU host (`worker-tests` runner) — see
`.github/workflows/bench.yml`. Failed regressions open an issue;
results are committed back to a `bench-results` branch on success.
