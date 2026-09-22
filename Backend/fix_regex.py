path = 'app/services/extractor.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(r'\\\\b', r'\b')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
