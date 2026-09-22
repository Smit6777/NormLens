import re
from pathlib import Path

path = Path('app/services/gap_analysis.py')
content = path.read_text(encoding='utf-8')

new_logic = """        # Deduplicate
        unique_gaps = []
        seen = set()
        for gap in gaps:
            std = gap.related_standards[0] if gap.related_standards else "none"
            identity = (gap.gap_type.value, std, gap.message.lower().strip())
            if identity not in seen:
                seen.add(identity)
                unique_gaps.append(gap)
        return unique_gaps"""

content = content.replace('        return gaps', new_logic)

path.write_text(content, encoding='utf-8')
print("Patched gap_analysis.py for deduplication")
