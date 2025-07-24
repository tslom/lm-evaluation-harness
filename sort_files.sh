#!/usr/bin/env bash
set -euo pipefail

# Determine the directory this script lives in, so paths are always correct
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
results_root="$script_dir/results_2"

# Loop over each model directory under results_2
for model_path in "$results_root"/*/; do
  model=$(basename "$model_path")

  # For each results_<ts>.json in that model
  for result in "$model_path"/results_*.json; do
    # Skip if no matches
    [[ -e $result ]] || continue

    # Extract timestamp (after "results_" before ".json")
    ts=$(basename "$result")
    ts=${ts#results_}
    ts=${ts%.json}

    # Gather all sample files matching that timestamp
    shopt -s nullglob
    samples=( "$model_path"/samples_*_"$ts".jsonl )
    shopt -u nullglob

    # If none, warn and skip
    if (( ${#samples[@]} == 0 )); then
      echo "⚠️  No samples for $result; skipping."
      continue
    fi

    # Derive benchmark from first sample: drop "samples_" then take up to first "_"
    fname=$(basename "${samples[0]}")
    benchmark=${fname#samples_}
    benchmark=${benchmark%%_*}

    # Prepare destination and move everything
    dest="$results_root/$benchmark/$model"
    mkdir -p "$dest"
    mv "$result" "${samples[@]}" "$dest/"

    echo "✅  Moved $(basename "$result") + ${#samples[@]} sample(s) → $dest/"
  done
done

echo "🎉 Reorganization complete!"
