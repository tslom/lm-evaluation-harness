from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from typing import Optional

from .flores_plus_eng_to_xx import FloresDatasetProcessor
from .solvers.direct_translation import direct_translation
from .solvers.few_shot_translation import few_shot_translation
from .solvers.zero_shot_translation import zero_shot_translation
from .solvers.pivot_translation import pivot_translation
from .scoring import bleu_translation

# Language code to name mapping for common languages
LANGUAGE_NAMES = {
    "fra": "French",
    "deu": "German", 
    "spa": "Spanish",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "zho": "Chinese",
    "jpn": "Japanese",
    "ara": "Arabic",
    "hin": "Hindi",
    "kor": "Korean",
    "nld": "Dutch",
    "pol": "Polish",
    "tur": "Turkish",
    "vie": "Vietnamese"
}

def load_flores_eng_to_target_dataset(
    target_lang: str,
    split: str = "dev",
    limit: Optional[int] = None,
    seed: int = 42
) -> MemoryDataset:
    """
    Load FLORES+ dataset for English to target language translation.
    
    Args:
        target_lang: Target language code (e.g., 'fra', 'deu') 
        split: Dataset split to use
        limit: Maximum number of samples to include
        seed: Random seed for reproducible sampling
    """
    from datasets import load_dataset
    import random
    
    processor = FloresDatasetProcessor()
    
    # Validate target language exists
    if target_lang not in processor.available_configs:
        raise ValueError(f"Target language '{target_lang}' not found in available configs")
    
    try:
        # Load the actual FLORES+ dataset
        dataset = load_dataset(
            processor.dataset_name,
            name=target_lang,
            split=split
        )
        
        # Convert dataset to list for sampling
        data_list = list(dataset)
        
        # Apply sampling with seed for reproducibility
        if seed is not None:
            random.seed(seed)
            random.shuffle(data_list)
        
        # Apply limit
        if limit is not None:
            data_list = data_list[:limit]
        
        # Create Sample objects from real data
        samples = []
        for idx, example in enumerate(data_list):
            # Try to extract English and target language text
            english_text = None
            target_text = None
            
            # Try different possible field names for English
            for eng_field in ['eng_Latn', 'eng', 'english', 'en']:
                if eng_field in example:
                    english_text = example[eng_field]
                    break
            
            # Try different possible field names for target language
            for target_field in [f'{target_lang}_Latn', target_lang, 'target', 'translation']:
                if target_field in example:
                    target_text = example[target_field]
                    break
            
            # If we found both texts, create a Sample
            if english_text is not None and target_text is not None:
                samples.append(Sample(
                    input=str(english_text).strip(),
                    target=str(target_text).strip(),
                    metadata={
                        "source_lang": "eng",
                        "target_lang": target_lang,
                        "sentence_id": idx,
                        "split": split
                    }
                ))
            else:
                # Log what fields are available for debugging
                print(f"Could not find English/target text in row {idx}. Available fields: {list(example.keys())}")
        
        if not samples:
            raise ValueError(f"No valid translation pairs found for {target_lang}")
        
        print(f"Loaded {len(samples)} translation pairs for eng→{target_lang}")
        return MemoryDataset(samples=samples, name=f"flores_eng_to_{target_lang}")
        
    except Exception as e:
        print(f"Error loading FLORES+ data: {e}")
        print("Falling back to placeholder data...")
        
        # Fallback to placeholder data if real data loading fails
        samples = [
            Sample(
                input="Hello, how are you?",
                target="Example target translation",
                metadata={
                    "source_lang": "eng",
                    "target_lang": target_lang,
                    "sentence_id": 0,
                    "split": split,
                    "is_placeholder": True
                }
            ),
            Sample(
                input="The weather is nice today.",
                target="Example target translation 2", 
                metadata={
                    "source_lang": "eng",
                    "target_lang": target_lang,
                    "sentence_id": 1,
                    "split": split,
                    "is_placeholder": True
                }
            )
        ]
        
        # Apply limit to placeholder data too
        if limit is not None:
            samples = samples[:limit]
        
        return MemoryDataset(samples=samples, name=f"flores_eng_to_{target_lang}")

@task
def flores_eng_to_target(
    target_language: str,
    solver_type: str = "direct",
    limit: Optional[int] = None,
    seed: int = 42,
    split: str = "dev"
) -> Task:
    """
    English to target language translation task.
    
    Args:
        target_language: Target language code (e.g., 'fra', 'deu', 'spa')
        solver_type: Type of solver ('direct', 'few_shot', 'zero_shot', 'pivot')
        limit: Maximum number of samples to evaluate
        seed: Random seed for reproducible results
        split: Dataset split to use
    """
    dataset = load_flores_eng_to_target_dataset(
        target_lang=target_language,
        split=split,
        limit=limit,
        seed=seed
    )
    
    # Get target language name
    target_lang_name = LANGUAGE_NAMES.get(target_language, target_language)
    
    # Select solver based on type
    if solver_type == "direct":
        solver = direct_translation(
            direction="eng_to_target",
            target_lang=target_lang_name,
            source_lang="English",
            target_lang_code=target_language,
            source_lang_code="eng"
        )
    elif solver_type == "few_shot":
        solver = few_shot_translation(
            direction="eng_to_target",
            target_lang=target_lang_name,
            source_lang="English",
            target_lang_code=target_language,
            source_lang_code="eng"
        )
    elif solver_type == "zero_shot": 
        solver = zero_shot_translation(
            direction="eng_to_target",
            target_lang=target_lang_name,
            source_lang="English",
            target_lang_code=target_language,
            source_lang_code="eng"
        )
    elif solver_type == "pivot":
        solver = pivot_translation(
            direction="eng_to_target",
            target_lang=target_lang_name,
            source_lang="English",
            target_lang_code=target_language,
            source_lang_code="eng"
        )
    else:
        raise ValueError(f"Unknown solver type: {solver_type}")
    
    return Task(
        dataset=dataset,
        solver=solver,
        scorer=bleu_translation(),
        name=f"flores_eng_to_{target_language}_{solver_type}"
    ) 