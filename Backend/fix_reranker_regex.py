path = 'app/services/reranker.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(r'r"\\b" + re.escape(f_stem) + r"s?\\b"', r'r"\b" + re.escape(f_stem) + r"s?\b"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
