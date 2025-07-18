set -euo pipefail

MODELS=(
  #"google/mt5-small"
  #"stanfordnlp/mrt5-small"
  "google/byt5-small"
  "meta-llama/Llama-3.2-3B"
)
TASKS=(
  "belebele"
  "global_mmlu"
  "lambada_multilingual_stablelm"
  "mgsm"
  "mlqa"
  "mmlu_prox"
  "okapi"
  #"paws-x"
  "truthfulqa-multi"
  "xcopa"
  "xnli"
  "xquad"
  "xstorycloze"
  "xwinograd"
)

for TASK in "${TASKS[@]}"; do
  for MODEL in "${MODELS[@]}"; do
    echo "Running $MODEL on $TASK"
    lm_eval \
      --model hf \
      --model_args pretrained=$MODEL,trust_remote_code=True \
      --device cuda \
      --batch_size auto:4 \
      --tasks "$TASK" \
      --output_path "results/${MODEL//\//_}/${TASK}" \
      --log_samples \
      --limit 2
  done
done
