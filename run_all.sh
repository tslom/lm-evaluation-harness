set +e

ERROR_LOG="all_errors.log"
: > "$ERROR_LOG"

MODELS=(
  "google/mt5-small"
  "stanfordnlp/mrt5-small"
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
LAMBADA=(
  "lambada_multilingual_stablelm_en"
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
  "mmlu_pro_ar"
  "mmlu_pro_bn"
  "mmlu_pro_de"
  "mmlu_pro_en"
  "mmlu_pro_es"
  "mmlu_pro_fr"
  "mmlu_pro_hi"
  "mmlu_pro_ja"
  "mmlu_pro_ko"
  "mmlu_pro_pt"
  "mmlu_pro_sw"
  "mmlu_pro_th"
  "mmlu_pro_zh"
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

#!/usr/bin/env bash
set -uo pipefail
# Don't exit on error so we can log and continue
# Initialize the error log
ERROR_LOG="logs/error.log"
mkdir -p "$(dirname "$ERROR_LOG")"


slugify() {
  echo "$1" | sed 's/[^a-zA-Z0-9]/_/g'
}

for TASK in "${XNLI[@]}"; do
  SAFE_TASK=$(slugify "$TASK")
  for MODEL in "${MODELS[@]}"; do
    SAFE_MODEL=$(slugify "$MODEL")
    echo "▶ Running ${MODEL} on ${TASK}…"

    MODEL_ARGS="pretrained=${MODEL},trust_remote_code=True"

    OUT_DIR="logs/${SAFE_MODEL}"
    mkdir -p ${OUT_DIR}
    LOG_FILE="${OUT_DIR}/${SAFE_TASK}.log"

    # Run the evaluation, capturing stdout+stderr
    lm_eval \
      --model hf \
      --model_args "$MODEL_ARGS" \
      --device cuda \
      --batch_size auto:4 \
      --num_fewshot 8
      --tasks "$TASK" \
      --output_path "results/${TASK}" \
      --log_samples \
      >"$LOG_FILE" 2>&1

    # Check exit status and log errors
    if [ $? -ne 0 ]; then
      echo "[ERROR] $MODEL × $TASK failed. See $LOG_FILE" | tee -a "$ERROR_LOG"
    else
      echo "[OK]    $MODEL × $TASK completed."
    fi
  done
done

echo "✅ All done. Any failures have been logged to $ERROR_LOG"

