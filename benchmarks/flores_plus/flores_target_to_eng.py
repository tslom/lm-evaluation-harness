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

def load_flores_target_to_eng_dataset(
    source_lang: str,
    split: str = "dev",
    limit: Optional[int] = None,
    seed: int = 42
) -> MemoryDataset:
    """
    Load FLORES+ dataset for target language to English translation.
    
    Args:
        source_lang: Source language code (e.g., 'fra', 'deu') 
        split: Dataset split to use
        limit: Maximum number of samples to include
        seed: Random seed for reproducible sampling
    """
    from datasets import load_dataset
    import random
    
    processor = FloresDatasetProcessor()
    
    # Validate source language exists
    if source_lang not in processor.available_configs:
        raise ValueError(f"Source language '{source_lang}' not found in available configs")
    
    try:
        # Load the actual FLORES+ dataset
        dataset = load_dataset(
            processor.dataset_name,
            name=source_lang,
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
            # Try to extract source language and English text
            source_text = None
            english_text = None
            
            # Try different possible field names for source language
            for source_field in [f'{source_lang}_Latn', source_lang, 'source']:
                if source_field in example:
                    source_text = example[source_field]
                    break
            
            # Try different possible field names for English
            for eng_field in ['eng_Latn', 'eng', 'english', 'en']:
                if eng_field in example:
                    english_text = example[eng_field]
                    break
            
            # If we found both texts, create a Sample
            if source_text is not None and english_text is not None:
                samples.append(Sample(
                    input=str(source_text).strip(),
                    target=str(english_text).strip(),
                    metadata={
                        "source_lang": source_lang,
                        "target_lang": "eng",
                        "sentence_id": idx,
                        "split": split
                    }
                ))
            else:
                # Log what fields are available for debugging
                print(f"Could not find source/English text in row {idx}. Available fields: {list(example.keys())}")
        
        if not samples:
            raise ValueError(f"No valid translation pairs found for {source_lang}")
        
        print(f"Loaded {len(samples)} translation pairs for {source_lang}→eng")
        return MemoryDataset(samples=samples, name=f"flores_{source_lang}_to_eng")
        
    except Exception as e:
        print(f"Error loading FLORES+ data: {e}")
        print("Falling back to placeholder data...")
        
        # Fallback to placeholder data if real data loading fails
        samples = [
            Sample(
                input="Example source language text",
                target="Hello, how are you?",
                metadata={
                    "source_lang": source_lang,
                    "target_lang": "eng",
                    "sentence_id": 0,
                    "split": split,
                    "is_placeholder": True
                }
            ),
            Sample(
                input="Example source language text 2",
                target="The weather is nice today.", 
                metadata={
                    "source_lang": source_lang,
                    "target_lang": "eng",
                    "sentence_id": 1,
                    "split": split,
                    "is_placeholder": True
                }
            )
        ]
        
        # Apply limit to placeholder data too
        if limit is not None:
            samples = samples[:limit]
        
        return MemoryDataset(samples=samples, name=f"flores_{source_lang}_to_eng")

@task 
def flores_target_to_eng(
    source_language: str,
    solver_type: str = "direct", 
    limit: Optional[int] = None,
    seed: int = 42,
    split: str = "dev"
) -> Task:
    """
    Target language to English translation task.
    
    Args:
        source_language: Source language code (e.g., 'fra', 'deu', 'spa')
        solver_type: Type of solver ('direct', 'few_shot', 'zero_shot', 'pivot')
        limit: Maximum number of samples to evaluate
        seed: Random seed for reproducible results
        split: Dataset split to use
    """
    dataset = load_flores_target_to_eng_dataset(
        source_lang=source_language,
        split=split,
        limit=limit,
        seed=seed
    )
    
    # Get source language name
    source_lang_name = LANGUAGE_NAMES.get(source_language, source_language)
    
    # Select solver based on type
    if solver_type == "direct":
        solver = direct_translation(
            direction="target_to_eng",
            target_lang="English",
            source_lang=source_lang_name,
            target_lang_code="eng",
            source_lang_code=source_language
        )
    elif solver_type == "few_shot":
        solver = few_shot_translation(
            direction="target_to_eng",
            target_lang="English",
            source_lang=source_lang_name,
            target_lang_code="eng",
            source_lang_code=source_language
        )
    elif solver_type == "zero_shot":
        solver = zero_shot_translation(
            direction="target_to_eng",
            target_lang="English",
            source_lang=source_lang_name,
            target_lang_code="eng",
            source_lang_code=source_language
        ) 
    elif solver_type == "pivot":
        solver = pivot_translation(
            direction="target_to_eng",
            target_lang="English",
            source_lang=source_lang_name,
            target_lang_code="eng",
            source_lang_code=source_language
        )
    else:
        raise ValueError(f"Unknown solver type: {solver_type}")
    
    return Task(
        dataset=dataset,
        solver=solver,
        scorer=bleu_translation(),
        name=f"flores_{source_language}_to_eng_{solver_type}"
    ) 