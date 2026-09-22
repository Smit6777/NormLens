import asyncio
import json
from app.services.extractor import RuleBasedRequirementExtractor
from app.services.reranker import Reranker
from app.models.schemas import ExtractedRequirement

# Mock vocab mapping
vocab = {
    "steel pipes": ("Steel Pipes", "Metal"),
    "steel bars": ("Steel Bars", "Metal"),
    "electrical panels": ("Electrical Panels", "Electrical"),
    "safety helmets": ("Safety Helmets", "Safety")
}

extractor = RuleBasedRequirementExtractor(vocabulary=vocab)

class MockPage:
    def __init__(self, text):
        self.text = text
        self.page_number = 1

def test_extract():
    reqs = extractor.extract([MockPage("Supply steel pipes, electrical panels and safety helmets.")])
    print(f"Extracted {len(reqs)} requirements:")
    for r in reqs:
        print(f"- {r.product} (form: {r.form}, material: {r.material}) from {r.raw_text}")

test_extract()
