import re
from pathlib import Path

path = Path('app/services/reranker.py')
content = path.read_text(encoding='utf-8')

# We need to pass the requirement object into _score or just extract cited_standards
new_score_logic = '''        kw_overlap = len(req_tokens & kw_terms) / max(1, len(req_tokens))
        components["keyword_overlap"] = kw_overlap
        if kw_overlap > 0: reasons.append(f"Shared keyword/title terms: {', '.join(req_tokens & kw_terms)}.")
        else: skipped.append("keyword overlap")

        # Check for cited standard bonus
        is_cited = False
        # We need cited_standards from somewhere. Wait, rerank_input has it.
        pass'''

# Actually, an easier way is to just inject a 10.0 score component if the semantic score is EXACTLY 1.0
# because in matcher.py we appended exact matches with semantic_score=1.0!

new_score_logic2 = '''        total = sum(components[k] * getattr(self._weights, k, 0.0) for k in components)
        if cand.semantic_score == 1.0:
            total += 10.0
            reasons.append("Direct citation match found in requirement.")
        
        return RerankedCandidate('''

content = re.sub(r'        total = sum\(components\[k\] \* getattr\(self\._weights, k, 0\.0\) for k in components\)\n        return RerankedCandidate\(', new_score_logic2, content)
path.write_text(content, encoding='utf-8')
print("Patched reranker.py")
