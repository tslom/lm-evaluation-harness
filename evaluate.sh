MODELS=(
  "stanfordnlp/mrt5-small"
  "google/mt5-small"
  "google/byt5-small"
  "meta-llama/Llama-3.2-3B"
)

BENCHMARKS=(
#  "BELEBELE"
#  "GLOBAL_MMLU"
#  "MLQA"
#  "MMLU_PRO_X"
#  "OKAPI"
#  "PAWS_X"
#  "TRUTHFULQA"
  "XCOPA"
  "XNLI"
  "XQUAD"
#  "XWINOGRAD"
)

STATUS_MD="run_status.md"
MARKER_DIR="markers"
LOG_DIR="orchestrator_logs"
mkdir -p "$MARKER_DIR" "$LOG_DIR"
echo "# Run Status" > "$STATUS_MD"
echo "" >> "$STATUS_MD"

# slugify helper
slugify(){ echo "$1" | sed 's/[^a-zA-Z0-9]/_/g'; }

for MODEL in "${MODELS[@]}"; do
  SAFE_MODEL=$(slugify "$MODEL")
  for BM in "${BENCHMARKS[@]}"; do
    SAFE_BM=$(slugify "$BM")
    MARKER="${MARKER_DIR}/${SAFE_MODEL}_${SAFE_BM}.done"
    LOGFILE="${LOG_DIR}/${SAFE_MODEL}_${SAFE_BM}.log"

    # Skip if already done
    if [[ -f "$MARKER" ]]; then
      echo "🔹 Skipping $MODEL × $BM (already done)" | tee -a "$LOGFILE"
      echo "- [x] **$MODEL** on **$BM** — _skipped_" >> "$STATUS_MD"
      continue
    fi

    echo "▶ Running $MODEL × $BM…" | tee -a "$LOGFILE"
    start=$(date +%s)

    # Call your existing driver
    if ./run_task.sh --model "$MODEL" --benchmark "$BM" 2>&1 | tee -a "$LOGFILE"; then
      end=$(date +%s)
      echo "- [x] **$MODEL** on **$BM** — ✅ $(date +'%Y-%m-%d %H:%M:%S') (took $((end-start))s)" >> "$STATUS_MD"
      touch "$MARKER"
    else
      end=$(date +%s)
      echo "- [ ] **$MODEL** on **$BM** — ❌ $(date +'%Y-%m-%d %H:%M:%S') (took $((end-start))s)" >> "$STATUS_MD"
    fi

    echo "" >> "$STATUS_MD"
  done
done

echo "✅ All combinations processed. See $STATUS_MD and $LOG_DIR for details."```