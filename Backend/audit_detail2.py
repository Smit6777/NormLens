import httpx
# Multi-product: should produce separate requirements
res = httpx.post('http://127.0.0.1:8000/api/v1/analyze', data={'text': 'Supply steel pipes, electrical panels and safety helmets.'}, headers={'X-API-Key': 'development_key'})
d = res.json()
reqs = d.get("requirements", [])
recs = d.get("recommendations", {})
print("Requirements:", len(reqs))
for req in reqs:
    print(f"  {req['requirement_id']}: product={req['product']} raw={req['raw_text'][:60]}")
    rid_recs = recs.get(req['requirement_id'], [])
    for r in rid_recs[:2]:
        print(f"    -> {r['is_number']} ({r['system_match_score']:.2f})")
print()

# Test 11: LED lighting returns EMPTY but has a real standard IS 10322
print("---")
res2 = httpx.post('http://127.0.0.1:8000/api/v1/analyze', data={'text': 'Supply LED street lighting luminaires suitable for outdoor roads.'}, headers={'X-API-Key': 'development_key'})
d2 = res2.json()
reqs2 = d2.get("requirements", [])
recs2 = d2.get("recommendations", {})
print("LED: Requirements:", len(reqs2))
for req in reqs2:
    print(f"  {req['requirement_id']}: product={req['product']} category={req['category']}")
    rid_recs = recs2.get(req['requirement_id'], [])
    if rid_recs:
        for r in rid_recs[:3]:
            print(f"    -> {r['is_number']} ({r['system_match_score']:.2f})")
    else:
        print(f"    -> EMPTY")
