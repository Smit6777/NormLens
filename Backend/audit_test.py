"""Adversarial audit test matrix."""
import httpx
import json

API = "http://127.0.0.1:8000/api/v1/analyze"
HDR = {"X-API-Key": "development_key"}

tests = [
    ("TEST 1: Laboratory equipment", "Procure advanced laboratory equipment."),
    ("TEST 2: Railway upholstery", "Fire-resistant interior seating materials for railway passenger coaches."),
    ("TEST 3: Medical diagnostic", "Supply high-precision medical diagnostic imaging equipment with AI-assisted image processing."),
    ("TEST 4: Steel pipes", "Supply steel pipes for water distribution network."),
    ("TEST 5: Electrical panel", "Supply electrical distribution panels for industrial building."),
    ("TEST 6: Unknown machine", "Supply advanced industrial processing machine with automated control."),
    ("TEST 7: Exact IS 8112", "Supply OPC 43 Grade cement conforming to IS 8112:2013."),
    ("TEST 8: Exact IS 2062", "Supply structural steel conforming to IS 2062."),
    ("TEST 9: Vague cement", "Supply good quality cement for government building work."),
    ("TEST 10: Multi-product", "Supply steel pipes, electrical panels and safety helmets."),
    ("TEST 11: LED lighting", "Supply LED street lighting luminaires suitable for outdoor roads."),
    ("TEST 12: TMT steel", "Supply TMT reinforcement steel bars Fe 500D."),
    ("TEST 13: IS8112 no space", "Supply cement conforming to IS8112."),
    ("TEST 14: IS 8112 : 2013 spaces", "Supply cement conforming to IS 8112 : 2013."),
    ("TEST 15: Unknown IS", "Supply material conforming to IS 99999."),
    ("TEST 16: Multiple IS", "Supply cement IS 8112 and steel IS 2062."),
    ("TEST 17: Empty text", ""),
    ("TEST 18: Agriculture", "Supply agricultural processing unit for rice milling."),
    ("TEST 19: Food", "Supply packaged drinking water."),
    ("TEST 20: Textile", "Supply polyester fabric for industrial use."),
]

for name, text in tests:
    if not text:
        res = httpx.post(API, data={"text": ""}, headers=HDR, timeout=30)
        print(f"{name}")
        print(f"  Status={res.status_code} Error={res.json().get('error', 'none')}")
        print()
        continue

    res = httpx.post(API, data={"text": text}, headers=HDR, timeout=30)
    d = res.json()
    reqs = d.get("requirements", [])
    all_recs = d.get("recommendations", {})
    gaps = d.get("gaps", [])

    rec_summary = []
    for req in reqs:
        rid = req["requirement_id"]
        recs = all_recs.get(rid, [])
        for r in recs[:3]:
            rec_summary.append(f"{r['is_number']}({r['system_match_score']:.2f})")

    product = reqs[0]["product"] if reqs else "NONE"
    category = reqs[0]["category"] if reqs else "NONE"
    gap_types = [g["gap_type"] for g in gaps]

    print(f"{name}")
    print(f"  Product={product} | Category={category}")
    if rec_summary:
        print(f"  Recs={rec_summary}")
    else:
        print(f"  Recs=EMPTY - NOT VERIFIED")
    print(f"  Gaps={gap_types}")
    print()
