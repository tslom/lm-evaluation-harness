"""
Translation scoring functions for FLORES+ benchmark.
"""

import math
from collections import Counter
from typing import List, Optional
from inspect_ai.scorer import Score, Scorer, Target
from inspect_ai.model import ModelOutput


def compute_bleu_score(
    candidate: str,
    references: List[str],
    max_n: int = 4
) -> float:
    """
    Compute BLEU score for a candidate translation against reference translations.
    
    Args:
        candidate: The machine-generated translation
        references: List of reference translations
        max_n: Maximum n-gram length to consider (default: 4)
        
    Returns:
        BLEU score between 0 and 1
    """
    if not candidate or not candidate.strip():
        return 0.0
    
    if not references or all(not ref or not ref.strip() for ref in references):
        return 0.0
    
    # Tokenize (simple whitespace tokenization)
    candidate_tokens = candidate.lower().split()
    reference_token_lists = [ref.lower().split() for ref in references if ref and ref.strip()]
    
    if not candidate_tokens or not reference_token_lists:
        return 0.0
    
    # Calculate n-gram precisions
    precisions = []
    
    for n in range(1, max_n + 1):
        # Get candidate n-grams
        candidate_ngrams = Counter()
        for i in range(len(candidate_tokens) - n + 1):
            ngram = tuple(candidate_tokens[i:i + n])
            candidate_ngrams[ngram] += 1
        
        if not candidate_ngrams:
            precisions.append(0.0)
            continue
        
        # Get maximum counts from all references
        max_reference_ngrams = Counter()
        for ref_tokens in reference_token_lists:
            ref_ngrams = Counter()
            for i in range(len(ref_tokens) - n + 1):
                ngram = tuple(ref_tokens[i:i + n])
                ref_ngrams[ngram] += 1
            
            # Take maximum count for each n-gram across references
            for ngram, count in ref_ngrams.items():
                max_reference_ngrams[ngram] = max(max_reference_ngrams[ngram], count)
        
        # Calculate clipped precision
        clipped_counts = 0
        total_counts = 0
        
        for ngram, count in candidate_ngrams.items():
            clipped_counts += min(count, max_reference_ngrams.get(ngram, 0))
            total_counts += count
        
        if total_counts == 0:
            precisions.append(0.0)
        else:
            precisions.append(clipped_counts / total_counts)
    
    # Calculate brevity penalty
    candidate_length = len(candidate_tokens)
    # Find closest reference length
    reference_lengths = [len(ref_tokens) for ref_tokens in reference_token_lists]
    if not reference_lengths:
        return 0.0
    
    closest_ref_length = min(reference_lengths, key=lambda x: abs(x - candidate_length))
    
    if candidate_length > closest_ref_length:
        brevity_penalty = 1.0
    elif candidate_length == 0:
        brevity_penalty = 0.0
    else:
        brevity_penalty = math.exp(1 - closest_ref_length / candidate_length)
    
    # Calculate geometric mean of precisions
    valid_precisions = [p for p in precisions if p > 0]
    if not valid_precisions:
        return 0.0
    
    # BLEU score is brevity penalty * geometric mean of precisions
    log_sum = sum(math.log(p) for p in valid_precisions)
    geometric_mean = math.exp(log_sum / len(valid_precisions))
    
    return brevity_penalty * geometric_mean


def bleu_translation() -> Scorer:
    """
    BLEU scorer for translation tasks.
    
    Computes BLEU score by comparing the model output against target translations.
    Supports multiple reference translations.
    """
    async def score(state, target: Target) -> Score:
        # Get the model's response
        if not state.output or not state.output.completion:
            return Score(
                value=0.0,
                metadata={"error": "No model output available"}
            )
        
        candidate = state.output.completion.strip()
        
        # Handle target - convert to list of strings
        references: List[str] = []
        if isinstance(target, str):
            references = [target]
        elif isinstance(target, list):
            references = [str(ref) for ref in target if ref is not None]
        else:
            # Convert Target object to string
            references = [str(target)]
        
        # Filter out empty references
        references = [ref for ref in references if ref and ref.strip()]
        
        if not references:
            return Score(
                value=0.0,
                metadata={"error": "No valid reference translations available"}
            )
        
        # Compute BLEU score
        bleu_score = compute_bleu_score(candidate, references)
        
        return Score(
            value=bleu_score,
            metadata={
                "candidate": candidate,
                "references": references,
                "bleu_score": bleu_score
            }
        )
    
    return score 