import re

path = 'tests/test_requirement_extraction.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'r = _extract("Cement and LED lamp shall conform to specification.", vocab=vocab)[0]\n    assert r.product == "Cement" and r.parameters["products_mentioned"] == ["Cement", "LED Lamp"]',
    'reqs = _extract("Cement and LED lamp shall conform to specification.", vocab=vocab)\n    assert len(reqs) == 2\n    assert reqs[0].product == "Cement"\n    assert reqs[1].product == "LED Lamp"'
)
text = text.replace('test_multiple_products_first_wins_others_recorded', 'test_multiple_products_extracted_separately')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated test")
