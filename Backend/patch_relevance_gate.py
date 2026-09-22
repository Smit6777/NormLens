import re
from pathlib import Path

path = Path('app/services/matcher.py')
content = path.read_text(encoding='utf-8')

# We need to filter anked before assigning to ecommendations.
new_logic = '''        if self._reranker is not None:
            ranked = self._reranker.rerank(rerank_input, candidates)
        else:
            ranked = [
                RerankedCandidate(
                    record=c.record, final_score=c.semantic_score,
                    components={"semantic_similarity": c.semantic_score},
                    not_evaluated=["reranker disabled"], reasons=["No reranking available."]
                ) for c in sorted(candidates, key=lambda x: x.semantic_score, reverse=True)
            ]

        # --- RELEVANCE GATE ---
        # Discard weak candidates that survived the vector search but failed the domain/product reranker.
        # Threshold: 0.45 final score (or 2.0 for exact citations).
        accepted = [r for r in ranked if r.final_score >= 0.45][:k]

        if not accepted:
            return MatchResult(
                MatchStatus.INSUFFICIENT_EVIDENCE,
                message="NO SUFFICIENTLY VERIFIED BIS STANDARD FOUND. Human verification required."
            )

        recommendations = [build_recommendation(r) for r in accepted]'''

content = re.sub(
    r'        if self\._reranker is not None:\n            ranked = self\._reranker\.rerank\(rerank_input, candidates\)\[:k\]\n        else:\n            ranked = \[\n                RerankedCandidate\(\n                    record=c\.record, final_score=c\.semantic_score,\n                    components=\{"semantic_similarity": c\.semantic_score\},\n                    not_evaluated=\["reranker disabled"\], reasons=\\["No reranking available\."\\]\n                \) for c in sorted\(candidates, key=lambda x: x\.semantic_score, reverse=True\)\[:k\]\n            \]\n\n        recommendations = \[build_recommendation\(r\) for r in ranked\]',
    new_logic,
    content
)

path.write_text(content, encoding='utf-8')
print("Patched matcher.py for Relevance Gate")
