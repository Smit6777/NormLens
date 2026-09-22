import httpx
# Check exact citation: IS 8112 should show match_type info, not fake score
res = httpx.post('http://127.0.0.1:8000/api/v1/analyze', data={'text': 'Supply OPC 43 Grade cement conforming to IS 8112:2013.'}, headers={'X-API-Key': 'development_key'})
d = res.json()
recs = d['recommendations'].get('REQ-001', [])
r = recs[0]  # IS 8112:2013 should be first
print("IS number:", r['is_number'])
print("System match score:", r['system_match_score'])
print("Score components:", r['score_components'])
print("Match reasons:", r['match_reasons'])
print()
print("Evidence count:", len(r.get('evidence', [])))
for e in r.get('evidence', []):
    print(f"  source_id={e.get('source_id')} url={e.get('source_url')} status={e.get('verification_status')}")
print()
print("Compliance:")
c = r.get('compliance', {})
print(f"  standard_status={c.get('standard_status')}")
print(f"  current_version={c.get('current_version')}")
print(f"  qco_applicable={c.get('qco_applicable')}")
print(f"  certification_required={c.get('certification_required')}")
print(f"  qco_details count={len(c.get('qco_details', []))}")
