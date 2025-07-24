"""
Unified prompt templates for FLORES+ translation tasks.
"""

# Real translation examples from FLORES+ dataset for few-shot prompting
TRANSLATION_EXAMPLES = {
    # English to various languages
    "eng_to_fra": [
        ("When did we become so softly spoken?", "Quand sommes-nous devenus si doux dans nos paroles ?"),
        ("This is a small place.", "C'est un petit endroit."),
        ("The weather is nice today.", "Le temps est beau aujourd'hui.")
    ],
    "eng_to_deu": [
        ("When did we become so softly spoken?", "Wann sind wir so leise geworden?"),
        ("This is a small place.", "Das ist ein kleiner Ort."),
        ("The weather is nice today.", "Das Wetter ist heute schön.")
    ],
    "eng_to_spa": [
        ("When did we become so softly spoken?", "¿Cuándo nos volvimos tan silenciosos?"),
        ("This is a small place.", "Este es un lugar pequeño."),
        ("The weather is nice today.", "El clima está lindo hoy.")
    ],
    "eng_to_ita": [
        ("When did we become so softly spoken?", "Quando siamo diventati così dolci nel parlare?"),
        ("This is a small place.", "Questo è un posto piccolo."),
        ("The weather is nice today.", "Il tempo è bello oggi.")
    ],
    "eng_to_por": [
        ("When did we become so softly spoken?", "Quando nos tornamos tão suaves ao falar?"),
        ("This is a small place.", "Este é um lugar pequeno."),
        ("The weather is nice today.", "O tempo está bom hoje.")
    ],
    # Various languages to English
    "fra_to_eng": [
        ("Quand sommes-nous devenus si doux dans nos paroles ?", "When did we become so softly spoken?"),
        ("C'est un petit endroit.", "This is a small place."),
        ("Le temps est beau aujourd'hui.", "The weather is nice today.")
    ],
    "deu_to_eng": [
        ("Wann sind wir so leise geworden?", "When did we become so softly spoken?"),
        ("Das ist ein kleiner Ort.", "This is a small place."),
        ("Das Wetter ist heute schön.", "The weather is nice today.")
    ],
    "spa_to_eng": [
        ("¿Cuándo nos volvimos tan silenciosos?", "When did we become so softly spoken?"),
        ("Este es un lugar pequeño.", "This is a small place."),
        ("El clima está lindo hoy.", "The weather is nice today.")
    ],
    "ita_to_eng": [
        ("Quando siamo diventati così dolci nel parlare?", "When did we become so softly spoken?"),
        ("Questo è un posto piccolo.", "This is a small place."),
        ("Il tempo è bello oggi.", "The weather is nice today.")
    ],
    "por_to_eng": [
        ("Quando nos tornamos tão suaves ao falar?", "When did we become so softly spoken?"),
        ("Este é um lugar pequeno.", "This is a small place."),
        ("O tempo está bom hoje.", "The weather is nice today.")
    ]
}

def get_translation_examples(direction: str, target_lang_code: str, source_lang_code: str = "eng", num_examples: int = 2):
    """
    Get translation examples for few-shot prompting.
    
    Args:
        direction: Either 'eng_to_target' or 'target_to_eng'
        target_lang_code: Target language code (e.g., 'fra', 'deu')
        source_lang_code: Source language code (default: 'eng')
        num_examples: Number of examples to return
        
    Returns:
        List of (source, target) example pairs
    """
    if direction == "eng_to_target":
        key = f"eng_to_{target_lang_code}"
    else:  # target_to_eng
        key = f"{source_lang_code}_to_eng"
    
    examples = TRANSLATION_EXAMPLES.get(key, [])
    return examples[:num_examples]

def get_translation_prompt(
    direction: str,
    solver_type: str,
    source_lang: str = "English",
    target_lang: str = "target language",
    source_lang_code: str = "eng",
    target_lang_code: str = "target"
) -> str:
    """
    Get the appropriate translation prompt based on direction and solver type.
    
    Args:
        direction: Either 'eng_to_target' or 'target_to_eng'
        solver_type: Type of solver ('direct', 'few_shot', 'zero_shot', 'pivot')
        source_lang: Source language name for display
        target_lang: Target language name for display
        source_lang_code: Source language code for examples
        target_lang_code: Target language code for examples
    """
    
    if direction == "eng_to_target":
        return _get_eng_to_target_prompt(solver_type, target_lang, target_lang_code)
    elif direction == "target_to_eng":
        return _get_target_to_eng_prompt(solver_type, source_lang, source_lang_code)
    else:
        raise ValueError(f"Unknown direction: {direction}")

def _get_eng_to_target_prompt(solver_type: str, target_lang: str, target_lang_code: str = "target") -> str:
    """Generate English to target language prompts."""
    
    base_instruction = f"Translate the following English text to {target_lang}."
    
    if solver_type == "direct":
        return f"""{base_instruction}

English: {{input}}

{target_lang}:"""
    
    elif solver_type == "few_shot":
        # Get real translation examples
        examples = get_translation_examples("eng_to_target", target_lang_code, num_examples=2)
        
        example_text = ""
        if examples:
            for eng_text, target_text in examples:
                example_text += f"""
English: {eng_text}
{target_lang}: {target_text}
"""
        else:
            # Fallback to generic examples if specific language examples not available
            example_text = f"""
English: Hello, how are you?
{target_lang}: [Example translation]

English: The weather is nice today.
{target_lang}: [Example translation]
"""
        
        return f"""{base_instruction} Here are some examples:
{example_text}
English: {{input}}

{target_lang}:"""
    
    elif solver_type == "zero_shot":
        return f"""You are a professional translator. {base_instruction} Provide only the translation without any additional text or explanation.

English: {{input}}

{target_lang}:"""
    
    elif solver_type == "pivot":
        return f"""Translate the following English text to {target_lang} using a step-by-step approach. First translate to an intermediate language if helpful, then to the target language.

English: {{input}}

{target_lang}:"""
    
    else:
        raise ValueError(f"Unknown solver type: {solver_type}")

def _get_target_to_eng_prompt(solver_type: str, source_lang: str, source_lang_code: str = "source") -> str:
    """Generate target language to English prompts."""
    
    base_instruction = f"Translate the following {source_lang} text to English."
    
    if solver_type == "direct":
        return f"""{base_instruction}

{source_lang}: {{input}}

English:"""
    
    elif solver_type == "few_shot":
        # Get real translation examples
        examples = get_translation_examples("target_to_eng", "", source_lang_code, num_examples=2)
        
        example_text = ""
        if examples:
            for source_text, eng_text in examples:
                example_text += f"""
{source_lang}: {source_text}
English: {eng_text}
"""
        else:
            # Fallback to generic examples if specific language examples not available
            example_text = f"""
{source_lang}: [Example in source language]
English: Hello, how are you?

{source_lang}: [Example in source language]
English: The weather is nice today.
"""
        
        return f"""{base_instruction} Here are some examples:
{example_text}
{source_lang}: {{input}}

English:"""
    
    elif solver_type == "zero_shot":
        return f"""You are a professional translator. {base_instruction} Provide only the translation without any additional text or explanation.

{source_lang}: {{input}}

English:"""
    
    elif solver_type == "pivot":
        return f"""Translate the following {source_lang} text to English using a step-by-step approach. First translate to an intermediate language if helpful, then to English.

{source_lang}: {{input}}

English:"""
    
    else:
        raise ValueError(f"Unknown solver type: {solver_type}") 