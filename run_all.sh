# Make sure this file is executable: chmod +x run_all.sh

# Define your models and tasks
MODELS=(
  "google/byt5-small",
  "google/mt5-small",
  "stanfordnlp/mrt5-small",
  "meta-llama/Llama-3.2-3B"
)
TASKS=(
  "global_mmlu",
  "paws-x",
  "truthfulqa-multi",
  "xcopa",
  "xnli",
  "xquad",
  "xwinograd",
  "lambada_multilingual",
  "execute",
  "flores_plus"
)

# Loop over models and tasks
for MODEL in "${MODELS[@]}"; do
  for TASK in "${TASKS[@]}"; do
    echo "Running $MODEL on $TASK..."
    lm_eval \
      --model "hf" \
      --model_args pretrained="$MODEL"
      --device cuda \
      --batch_size auto:4 \
      --tasks "$TASK" \
      --outfile "results_${MODEL//\//_}_${TASK}.json"
  done
done
