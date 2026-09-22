import re
from pathlib import Path

path = Path('app/services/matcher.py')
content = path.read_text(encoding='utf-8')

new_logic = """        # --- RELEVANCE GATE ---
        accepted = [r for r in ranked if r.final_score >= 0.45]
        
        if not accepted:
            return MatchResult(
                MatchStatus.INSUFFICIENT_EVIDENCE,
                message="NO SUFFICIENTLY VERIFIED BIS STANDARD FOUND. Human verification required."
            )
            
        return MatchResult(MatchStatus.OK, [self._to_recommendation(r) for r in accepted])"""

content = content.replace('        return MatchResult(MatchStatus.OK, [self._to_recommendation(r) for r in ranked])', new_logic)

path.write_text(content, encoding='utf-8')
print("Patched matcher.py for Relevance Gate")
