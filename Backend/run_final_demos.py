import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/analyze"

demos = [
    {
        "name": "Demo 1 - Steel Pipe",
        "text": "Procurement of high-strength steel pipes for a water-supply infrastructure project. The pipes shall be circular, suitable for pressure applications, corrosion resistant, and supplied with appropriate testing certificates."
    },
    {
        "name": "Demo 2 - Cement",
        "text": "Procurement of Ordinary Portland Cement, 43 Grade, conforming to IS 8112:2013. The material shall satisfy the applicable testing and certification requirements."
    },
    {
        "name": "Demo 3 - Steel Pipe (Again)",
        "text": "Procurement of high-strength steel pipes for a water-supply infrastructure project. The pipes shall be circular, suitable for pressure applications, corrosion resistant, and supplied with appropriate testing certificates."
    },
    {
        "name": "Demo 4 - Safety Helmet",
        "text": "Procurement of industrial electrical safety helmets for workers at a manufacturing facility. The helmets shall provide protection against electrical hazards and mechanical impact and shall be supplied with appropriate testing certificates."
    }
]

for demo in demos:
    print(f"\\n{'='*50}")
    print(f"RUNNING: {demo['name']}")
    try:
        r = requests.post(BASE_URL, data={"text": demo["text"]})
        data = r.json()
        reqs = data.get("requirements", [])
        print(f"Total Requirements: {len(reqs)}")
        for i, req in enumerate(reqs):
            print(f"  Req {i+1}: Product={req.get('product')}, Canonical={req.get('canonical_product')}")
            print(f"         Explicit IS={req.get('parameters', {}).get('cited_standards', [])}")
            print(f"         Constraints={req.get('constraints')}")
        
        recs = data.get("recommendations", {})
        for req_id, items in recs.items():
            print(f"  Recs for {req_id}: {len(items)}")
            if items:
                print(f"    Top Match: {items[0].get('is_number')} (Score: {items[0].get('system_match_score')})")
                print(f"    QCO Applicable: {items[0].get('compliance', {}).get('qco_applicable')}")
                edges = items[0].get('compliance', {}).get('normative_relationships', [])
                print(f"    Normative Edges: {len(edges)}")
                for edge in edges:
                    print(f"      -> {edge.get('to_is')} ({edge.get('relationship_type')})")
        
        gaps = data.get("gaps", [])
        print(f"  Gaps: {len(gaps)}")
        for g in gaps:
            print(f"    - {g.get('gap_type')}: {g.get('message')}")
            
    except Exception as e:
        print(f"FAILED: {e}")
