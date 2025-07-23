import os
import shutil
import yaml

# Mapping of full language names to two‑letter codes (EXECUTE uses ISO 639‑1)
language_word_to_abbr = {
    "Amharic": "amh",
    "Arabic": "ara",
    "German": "deu",
    "English": "eng",
    "Hindi": "hin",
    "Japanese": "jpn",
    "Korean": "kor",
    "Russian": "rus",
    "Santali": "sat",
    "Spanish": "spa",
    "Tamazight": "tzm",
    "Xhoza": "xho",
    "Chinese": "zh",
}
language_abbr_to_word = {v: k for k, v in language_word_to_abbr.items()}

# Paths for LM-Eval-harness tasks and EXECUTE data
harness_tasks_dir = os.getcwd()
execute_data_dir = os.path.join(harness_tasks_dir + "/EXECUTE/data/tasks")

# Discover available languages and task types from the EXECUTE data folder
langs = [d for d in os.listdir(execute_data_dir) if os.path.isdir(os.path.join(execute_data_dir, d))]
task_types = sorted({
    fname.replace(".tsv", "")
    for lang in langs
    for fname in os.listdir(os.path.join(execute_data_dir, lang))
    if fname.endswith(".tsv")
})

print(task_types)

# Ensure base template exists
base_template = os.path.join(harness_tasks_dir, "_execute_template.yaml")
if not os.path.isfile(base_template):
    raise FileNotFoundError(f"Please create a base template at {base_template}")

for lang in langs:
    # Create a directory per language under harness tasks
    lang_dir = os.path.join(harness_tasks_dir, lang)
    os.makedirs(lang_dir, exist_ok=True)

    out_tmpl = os.path.join(lang_dir, f"_{lang}_template.yaml")
    with open(base_template, "r", encoding="utf-8") as reader, \
         open(out_tmpl, "w", encoding="utf-8") as writer:
        for line in reader:
            writer.write(line.replace("{lang}", lang))

    shutil.copy(os.path.join(harness_tasks_dir, "utils.py"), os.path.join(lang_dir, "utils.py"))

    group_name = f"execute_{lang}"
    group_dict = {
        "group": group_name,
        "task": [f"{group_name}_{tt}" for tt in task_types],
        "aggregate_metric_list": [
            {
                "aggregation": "mean",
                "metric": "exact_match",
                "weight_by_size": True,
                "filter_list": "custom-extract"
            }
        ],
        "metadata": {"version": 0.0}
    }
    with open(os.path.join(lang_dir, f"_{group_name}.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(group_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    for tt in task_types:
        sbj_yaml = {
            "description": f"EXECUTE task '{tt}' in {language_abbr_to_word.get(lang, lang)}",
            "include": f"_{lang}_template.yaml",
            "task": f"{group_name}_{tt}"
        }
        path = os.path.join(lang_dir, f"{group_name}_{tt}.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(sbj_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Generated configs for EXECUTE [{lang}] with {len(task_types)} tasks.")
