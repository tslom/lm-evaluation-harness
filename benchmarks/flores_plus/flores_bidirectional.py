from inspect_ai import Task
from typing import List, Optional

from .flores_eng_to_target import flores_eng_to_target
from .flores_target_to_eng import flores_target_to_eng

def flores_bidirectional(
    language: str,
    solver_type: str = "direct",
    limit: Optional[int] = None, 
    seed: int = 42,
    split: str = "dev"
) -> List[Task]:
    """
    Bidirectional translation tasks (both English↔Target).
    
    Args:
        language: Language code (e.g., 'fra', 'deu', 'spa')
        solver_type: Type of solver ('direct', 'few_shot', 'zero_shot', 'pivot')
        limit: Maximum number of samples to evaluate per direction
        seed: Random seed for reproducible results
        split: Dataset split to use
        
    Returns:
        List of tasks for both translation directions
    """
    return [
        flores_eng_to_target(language, solver_type, limit, seed, split),
        flores_target_to_eng(language, solver_type, limit, seed, split)
    ] 