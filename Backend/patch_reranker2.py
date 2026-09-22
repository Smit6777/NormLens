import re
from pathlib import Path

path = Path('app/services/reranker.py')
content = path.read_text(encoding='utf-8')

new_logic = '''        weights = self._weights.as_dict()
        total = sum(weights[name] for name in components)
        final = sum(weights[name] * value for name, value in components.items()) / total
        
        if cand.semantic_score == 1.0:
            final = 2.0  # Force it above all semantic hits (which max out at 1.0)
            reasons.append("Direct standard citation explicitly mapped to local knowledge base.")

        return RerankedCandidate('''

content = re.sub(r'        weights = self\._weights\.as_dict\(\)\n        total = sum\(weights\[name\] for name in components\)\n        final = sum\(weights\[name\] \* value for name, value in components\.items\(\)\) / total\n        return RerankedCandidate\(', new_logic, content)
path.write_text(content, encoding='utf-8')
print("Patched reranker.py again")
