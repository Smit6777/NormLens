import re

path = 'app/services/extractor.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'_FORMS_RE = re\.compile\(r".*?", re\.IGNORECASE\)',
    r'_FORMS_RE = re.compile(r"\\b(pipe|tube|bar|rod|plate|sheet|wire|cable|bolt|nut|beam|section|panel|helmet|glove|cement|pump|valve|motor|transformer)s?\\b", re.IGNORECASE)',
    text
)
text = re.sub(
    r'_MATERIALS_RE = re\.compile\(r".*?", re\.IGNORECASE\)',
    r'_MATERIALS_RE = re.compile(r"\\b(steel|iron|copper|aluminum|aluminium|plastic|pvc|hdpe|wood|glass|rubber|cotton)\\b", re.IGNORECASE)',
    text
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
