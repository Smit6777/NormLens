path = 'app/services/reranker.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'if re.search(' in line and 'all_cand_text):' in line:
        lines[i] = '                if re.search(r"\\b" + re.escape(f_stem) + r"s?\\b", all_cand_text):\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Done")
