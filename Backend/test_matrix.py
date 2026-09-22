import requests
import json

queries = [
    "Supply steel pipes.",
    "Supply steel bars.",
    "Supply steel pipes, electrical panels and safety helmets.",
    "Supply 43 Grade Ordinary Portland Cement conforming to IS 8112:2013.",
    "Procure advanced laboratory equipment.",
    "Supply fire-resistant railway passenger coach upholstery.",
    "Unknown industrial machine."
]

for i, q in enumerate(queries):
    print(f"\\n{'='*50}\\nTEST {i+1}: {q}\\n{'='*50}")
    res = requests.post("http://127.0.0.1:8000/api/v1/analyze", data={"text": q})
    try:
        data = res.json()
        reqs = data.get("requirements", [])
        print(f"Extracted {len(reqs)} requirements.")
        for r in reqs:
            print(f"- {r.get('product', 'NOT VERIFIED')} (Form: {r.get('form')}, Material: {r.get('material')})")
            
        recs = data.get("recommendations", {})
        for req_id, items in recs.items():
            print(f"Recommendations for {req_id}:")
            for item in items[:2]:
                print(f"  [{item['is_number']}] {item['title']} - Score: {item['system_match_score']:.2f}")
                print(f"    Reasons: {item.get('match_reasons', [])[:2]}")
    except Exception as e:
        print("Error:", e, res.text)
