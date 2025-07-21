set +e

ERROR_LOG="all_errors.log"
: > "$ERROR_LOG"

MODELS=(
  "stanfordnlp/mrt5-small"
  "google/mt5-small"
  "google/byt5-small"
  "meta-llama/Llama-3.2-3B"
)
BELEBELE=(
  "belebele"
)
GLOBAL_MMLU=(
  "global_mmlu_full_am"
  "global_mmlu_full_ar"
  "global_mmlu_full_bn"
  "global_mmlu_full_cs"
  "global_mmlu_full_de"
  "global_mmlu_full_el"
  "global_mmlu_full_en"
  "global_mmlu_full_es"
  "global_mmlu_full_fa"
  "global_mmlu_full_fil"
  "global_mmlu_full_fr"
  "global_mmlu_full_ha"
  "global_mmlu_full_he"
  "global_mmlu_full_hi"
  "global_mmlu_full_id"
  "global_mmlu_full_ig"
  "global_mmlu_full_it"
  "global_mmlu_full_ja"
  "global_mmlu_full_ko"
  "global_mmlu_full_ky"
  "global_mmlu_full_lt"
  "global_mmlu_full_mg"
  "global_mmlu_full_ms"
  "global_mmlu_full_ne"
  "global_mmlu_full_nl"
  "global_mmlu_full_ny"
  "global_mmlu_full_pt"
  "global_mmlu_full_ro"
  "global_mmlu_full_ru"
  "global_mmlu_full_si"
  "global_mmlu_full_sn"
  "global_mmlu_full_so"
  "global_mmlu_full_sr"
  "global_mmlu_full_sv"
  "global_mmlu_full_sw"
  "global_mmlu_full_te"
  "global_mmlu_full_tr"
  "global_mmlu_full_uk"
  "global_mmlu_full_vi"
  "global_mmlu_full_yo"
  "global_mmlu_full_zh"
)
MGSM=(
  "mgsm_direct"
  "mgsm_cot_native"
)
MLQA=(
  "mlqa_ar_ar"
  "mlqa_ar_de"
  "mlqa_ar_en"
  "mlqa_ar_es"
  "mlqa_ar_hi"
  "mlqa_ar_vi"
  "mlqa_ar_zh"
  "mlqa_de_ar"
  "mlqa_de_de"
  "mlqa_de_en"
  "mlqa_de_es"
  "mlqa_de_hi"
  "mlqa_de_vi"
  "mlqa_de_zh"
  "mlqa_en_ar"
  "mlqa_en_de"
  "mlqa_en_en"
  "mlqa_en_es"
  "mlqa_en_hi"
  "mlqa_en_vi"
  "mlqa_en_zh"
  "mlqa_es_ar"
  "mlqa_es_de"
  "mlqa_es_en"
  "mlqa_es_es"
  "mlqa_es_hi"
  "mlqa_es_vi"
  "mlqa_es_zh"
  "mlqa_hi_ar"
  "mlqa_hi_de"
  "mlqa_hi_en"
  "mlqa_hi_es"
  "mlqa_hi_hi"
  "mlqa_hi_vi"
  "mlqa_hi_zh"
  "mlqa_vi_ar"
  "mlqa_vi_de"
  "mlqa_vi_en"
  "mlqa_vi_es"
  "mlqa_vi_hi"
  "mlqa_vi_vi"
  "mlqa_vi_zh"
  "mlqa_zh_ar"
  "mlqa_zh_de"
  "mlqa_zh_en"
  "mlqa_zh_es"
  "mlqa_zh_hi"
  "mlqa_zh_vi"
  "mlqa_zh_zh"
)

MMLU_PRO_X=(
  "mmlu_prox_ar"
  "mmlu_prox_bn"
  "mmlu_prox_de"
  "mmlu_prox_en"
  "mmlu_prox_es"
  "mmlu_prox_fr"
  "mmlu_prox_hi"
  "mmlu_prox_ja"
  "mmlu_prox_ko"
  "mmlu_prox_pt"
  "mmlu_prox_sw"
  "mmlu_prox_th"
  "mmlu_prox_zh"
)

OKAPI=(
  "arc_multilingual"
  "hellaswag_multilingual"
  "truthfulqa_multilingual"
)

PAWS_X=(
  "pawsx"
)

TRUTHFULQA=(
  "truthfulqa-multi"
)

XCOPA=(
  "xcopa"
)

XNLI=(
  "xnli"
  "xnli_eu"
  "xnli_eu_mt"
  "xnli_eu_native"
)

XQUAD=(
  "xquad"
)

XWINOGRAD=(
  "xwinograd"
)

set -uo pipefail

MODEL=""
BENCHMARK_GROUPS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--model)
      MODEL="$2"; shift 2;;
    -b|--benchmark)
      BENCHMARK_GROUPS="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 --model <model_name> --benchmark <BELEBELE|GLOBAL_MMLU|MGSM|…>"
      exit 0;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 --model <model_name> --benchmark <BELEBELE|GLOBAL_MMLU|…>" >&2
      exit 1;;
  esac
done

if [[ -z "$MODEL" || -z "$BENCHMARK_GROUPS" ]]; then
  echo "Error: both --model and --benchmark are required." >&2
  exit 1
fi

case "${BENCHMARK_GROUPS,,}" in
  belebele)
    TASKS_CSV=$(IFS=,; echo "${BELEBELE[*]}")
    ;;
  global_mmlu)
    TASKS_CSV=$(IFS=,; echo "${GLOBAL_MMLU[*]}")
    ;;
  mgsm)
    TASKS_CSV=$(IFS=,; echo "${MGSM[*]}")
    ;;
  mlqa)
    TASKS_CSV=$(IFS=,; echo "${MLQA[*]}")
    ;;
  mmlu_prox)
    TASKS_CSV=$(IFS=,; echo "${MMLU_PRO_X[*]}")
    ;;
  okapi)
    TASKS_CSV=$(IFS=,; echo "${OKAPI[*]}")
    ;;
  pawsx)
    TASKS_CSV=$(IFS=,; echo "${PAWS_X[*]}")
    ;;
  truthfulqa-multi|truthfulqa_multi)
    TASKS_CSV=$(IFS=,; echo "${TRUTHFULQA[*]}")
    ;;
  xcopa)
    TASKS_CSV=$(IFS=,; echo "${XCOPA[*]}")
    ;;
  xnli)
    TASKS_CSV=$(IFS=,; echo "${XNLI[*]}")
    ;;
  xquad)
    TASKS_CSV=$(IFS=,; echo "${XQUAD[*]}")
    ;;
  xwinograd)
    TASKS_CSV=$(IFS=,; echo "${XWINOGRAD[*]}")
    ;;
  *)
    echo "Error: unknown benchmark '${BENCHMARK_GROUPS}'" >&2
    exit 1
    ;;
esac

ERROR_LOG="logs/error.log"
mkdir -p "$(dirname "$ERROR_LOG")"
: > "$ERROR_LOG"

slugify() {
  echo "$1" | sed 's/[^a-zA-Z0-9]/_/g'
}

SAFE_MODEL=$(slugify "$MODEL")
echo "▶ Running ${MODEL}"

if [[ "$MODEL" == "stanfordnlp/mrt5-small" ]]; then
  MODEL_ARGS="pretrained=${MODEL},trust_remote_code=True,backend=seq2seq"
else
  MODEL_ARGS="pretrained=${MODEL},trust_remote_code=True"
fi

OUT_DIR="logs/${SAFE_MODEL}"
mkdir -p "${OUT_DIR}"
LOG_FILE="${OUT_DIR}.log"

echo "Logging to ${LOG_FILE}"

if lm_eval \
     --model hf \
     --model_args "$MODEL_ARGS" \
     --device cuda \
     --batch_size 96 \
     --num_fewshot 0 \
     --tasks "$TASKS_CSV" \
     --output_path "results_2" \
     --log_samples \
     2>&1 | tee "$LOG_FILE"
then
  echo "[OK] ${MODEL}"
else
  echo "[ERROR] ${MODEL} (see ${LOG_FILE})" | tee -a "$ERROR_LOG"
fi

echo "✅ All done. Any failures have been logged to ${ERROR_LOG}"