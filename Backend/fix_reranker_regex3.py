import re

path = 'app/services/reranker.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# We know the line has 'cand_forms.add' inside the loop.
# Let's just find the loop and replace the whole if statement.
old_loop = """            for f in forms:
                f_stem = _stem(f)"""

# Instead of relying on matching the exact corrupted string, I'll just replace the whole block.
new_block = """            for f in forms:
                f_stem = _stem(f)
                if re.search(r"\\b" + re.escape(f_stem) + r"s?\\b", all_cand_text):
                    cand_forms.add(f_stem)"""

text = re.sub(r'            for f in forms:\n                f_stem = _stem\(f\)\n                if re\.search\(.*?\):\n                    cand_forms\.add\(f_stem\)', new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
