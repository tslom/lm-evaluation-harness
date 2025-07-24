MODELS=(
  "stanfordnlp/mrt5-large"
  "google/mt5-large"
  "google/byt5-large"
  "meta-llama/Llama-3.2-1B"
)

BENCHMARKS=(
#  "BELEBELE"
  "GLOBAL_MMLU"
#  "MLQA"
#  "MMLU_PRO_X"
  "PAWSX"
#  "OKAPI"
  "XCOPA"
  "XNLI"
  "XQUAD"
  "XWINOGRAD"
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

    ./run_task.sh --model "$MODEL" --benchmark "$BM" 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=${PIPESTATUS[0]}

    if [ $EXIT_CODE -eq 0 ]; then
      echo "- [x] **$MODEL** on **$BM** — ✅ $(date +'%Y-%m-%d %H:%M:%S')" >> "$STATUS_MD"
      touch "$MARKER"
    else
      echo "- [ ] **$MODEL** on **$BM** — ❌ $(date +'%Y-%m-%d %H:%M:%S')" >> "$STATUS_MD"
      echo "[ERROR] $MODEL × $BM failed (exit $EXIT_CODE)" | tee -a "$ERROR_LOG"
    fi
  done
done

echo "✅ All combinations processed. See $STATUS_MD and $LOG_DIR for details."