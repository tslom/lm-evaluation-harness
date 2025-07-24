from inspect_ai.solver import Solver, solver, prompt_template
from ..prompts import get_translation_prompt

@solver
def few_shot_translation(direction: str = "eng_to_target", target_lang: str = "target language", source_lang: str = "source language", target_lang_code: str = "target", source_lang_code: str = "source") -> Solver:
    """
    Few-shot translation solver for FLORES+ benchmark.
    
    Args:
        direction: Either 'eng_to_target' or 'target_to_eng'
        target_lang: Target language name for prompts
        source_lang: Source language name for prompts
        target_lang_code: Target language code for examples
        source_lang_code: Source language code for examples
    """
    prompt_template_str = get_translation_prompt(
        direction=direction,
        solver_type="few_shot",
        source_lang=source_lang,
        target_lang=target_lang,
        source_lang_code=source_lang_code,
        target_lang_code=target_lang_code
    )
    
    return prompt_template(prompt_template_str) 