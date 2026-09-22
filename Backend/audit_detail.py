import httpx
res = httpx.post('http://127.0.0.1:8000/api/v1/analyze', data={'text': 'Supply steel pipes for water distribution network.'}, headers={'X-API-Key': 'development_key'})
recs = res.json()['recommendations'].get('REQ-001', [])
for r in recs:
    print(r["is_number"], "|", r["title"], "| score=", round(r["system_match_score"], 2))
    print("  reasons:", r["match_reasons"][:2])
    print()
