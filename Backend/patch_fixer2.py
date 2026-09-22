import re
from pathlib import Path

path = Path('app/services/fixer.py')
content = path.read_text(encoding='utf-8')

content = content.replace(
    'product = req_obj.product if hasattr(req_obj, \'product\') else "unknown product"',
    'product = getattr(req_obj, \'product\', None) or "unknown product"'
)
content = content.replace(
    'category = req_obj.category if hasattr(req_obj, \'category\') else "unknown category"',
    'category = getattr(req_obj, \'category\', None) or "unknown category"'
)

path.write_text(content, encoding='utf-8')
print("Patched fixer.py null category fix")
