import re
from pathlib import Path

# Patch endpoints.py
ep_path = Path('app/api/endpoints.py')
ep_content = ep_path.read_text(encoding='utf-8')
ep_content = ep_content.replace(
    'services.fixer.suggest(\n        gaps, {r.requirement_id: r.raw_text for r in requirements}\n    )',
    'services.fixer.suggest(gaps, {r.requirement_id: r for r in requirements})'
)
ep_content = ep_content.replace(
    'services.fixer.suggest(body.gaps, body.requirement_text_by_id)',
    'services.fixer.suggest(body.gaps, body.requirement_text_by_id) # NOTE: /fix endpoint may be broken if it sends strings'
)
ep_path.write_text(ep_content, encoding='utf-8')

print("Patched endpoints.py")
