"""
semantic.py: Optional semantic skill similarity using SentenceTransformers with
robust, automatic fallback to deterministic string similarity when unavailable.
"""

from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple
from skilltrace_ai.normalization import normalize_skill_name

# Cached model instance for performance
_SEMANTIC_MODEL = None
_MODEL_TRIED = False


def _get_sentence_transformer_model():
    """Lazily loads SentenceTransformer if available in environment."""
    global _SEMANTIC_MODEL, _MODEL_TRIED
    if not _MODEL_TRIED:
        _MODEL_TRIED = True
        try:
            from sentence_transformers import SentenceTransformer
            _SEMANTIC_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _SEMANTIC_MODEL = None
    return _SEMANTIC_MODEL


def token_similarity(str1: str, str2: str) -> float:
    """
    Deterministic fallback similarity based on Levenshtein and token overlap.
    Returns a score between 0.0 and 1.0.
    """
    s1 = normalize_skill_name(str1)
    s2 = normalize_skill_name(str2)

    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    # Sequence matcher ratio
    seq_ratio = SequenceMatcher(None, s1, s2).ratio()

    # Word/token set overlap (Jaccard similarity on tokens)
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    if tokens1 and tokens2:
        overlap = len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
    else:
        overlap = 0.0

    # Weighted combined metric
    combined = max(seq_ratio, (seq_ratio * 0.5) + (overlap * 0.5))
    return round(combined, 3)


def find_semantic_match(
    target_skill: str,
    candidate_skills: List[Dict[str, Any]],
    threshold: float = 0.75,
) -> Tuple[Optional[Dict[str, Any]], float, str]:
    """
    Finds the closest semantic match for a target skill among candidate skills.
    Uses SentenceTransformer if available, otherwise deterministic string metrics.
    Returns: (matched_candidate_dict, similarity_score, method_used)
    """
    if not target_skill or not candidate_skills:
        return None, 0.0, "none"

    norm_target = normalize_skill_name(target_skill)
    model = _get_sentence_transformer_model()

    best_match: Optional[Dict[str, Any]] = None
    best_score: float = 0.0
    method = "fallback_token_similarity"

    if model is not None:
        try:
            from sentence_transformers import util
            target_emb = model.encode(norm_target, convert_to_tensor=True)
            candidate_names = [normalize_skill_name(c.get("name", "")) for c in candidate_skills]
            candidate_embs = model.encode(candidate_names, convert_to_tensor=True)

            cosine_scores = util.cos_sim(target_emb, candidate_embs)[0]
            for i, score_tensor in enumerate(cosine_scores):
                score = float(score_tensor.item())
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = candidate_skills[i]
            method = "sentence_transformers_minilm"
            return best_match, round(best_score, 3), method
        except Exception:
            # If embedding computation encounters an issue, gracefully continue to fallback
            pass

    # Deterministic fallback
    for candidate in candidate_skills:
        cand_name = candidate.get("name", "")
        score = token_similarity(norm_target, cand_name)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate

    return best_match, round(best_score, 3), method
