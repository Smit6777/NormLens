import re
from pathlib import Path

path = Path('app/services/matcher.py')
content = path.read_text(encoding='utf-8')

# Fix the requirement.cited_standards to requirement.parameters.get("cited_standards", [])
content = content.replace('if requirement.cited_standards:', 'if requirement.parameters.get("cited_standards"):')
content = content.replace('for cited in requirement.cited_standards:', 'for cited in requirement.parameters.get("cited_standards", []):')

path.write_text(content, encoding='utf-8')
print("Patched matcher.py for exact lookup")
