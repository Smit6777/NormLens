import re
from pathlib import Path

path = Path('app/services/matcher.py')
content = path.read_text(encoding='utf-8')

# We need to inject logic into match_requirement
new_match_req = '''    def match_requirement(self, requirement: ExtractedRequirement, top_k: int | None = None) -> MatchResult:
        \"\"\"Match a structured requirement; its product/category also feed the reranker.\"\"\"
        if not requirement.raw_text.strip():
            return MatchResult(MatchStatus.INSUFFICIENT_EVIDENCE, message="Empty requirement text.")
            
        exact_candidates = []
        if requirement.cited_standards:
            from app.data_layer.repository import normalize_is_number
            for cited in requirement.cited_standards:
                canon = normalize_is_number(cited)
                if canon:
                    record = self._repo.get_standard(canon)
                    if record:
                        # Append as a perfect semantic match (1.0)
                        exact_candidates.append(ScoredCandidate(record=record, semantic_score=1.0))
        
        return self._run(build_requirement_search_text(requirement), requirement, top_k, exact_candidates)'''

content = re.sub(r'    def match_requirement\(self.*?return self\._run\(build_requirement_search_text\(requirement\), requirement, top_k\)', new_match_req, content, flags=re.DOTALL)

# Now update _run to accept exact_candidates
new_run = '''    def _run(self, query_text: str, rerank_input: "ExtractedRequirement | str", top_k: int | None, exact_candidates: list[ScoredCandidate] = None) -> MatchResult:
        k = top_k or self._top_k
        pool = k * self._retrieval_multiplier if self._reranker else k
        hits = self._store.search(self._embeddings.generate_embedding(query_text), pool)

        candidates: list[ScoredCandidate] = exact_candidates or []
        existing_ids = {c.record["is_number"] for c in candidates}
        
        for hit in hits:
            if hit.score < self._min_score:
                continue
            record = self._repo.get_standard(hit.id)
            if record is None:  # stale index entry: never surface it
                logger.warning("Index hit not in repository; dropped", extra={"context": {"id": hit.id}})
                continue
            if record["is_number"] not in existing_ids:
                candidates.append(ScoredCandidate(record=record, semantic_score=hit.score))
                existing_ids.add(record["is_number"])'''

content = re.sub(r'    def _run\(self, query_text: str, rerank_input: "ExtractedRequirement \| str", top_k: int \| None\) -> MatchResult:.*?continue\n            candidates\.append\(ScoredCandidate\(record=record, semantic_score=hit\.score\)\)', new_run, content, flags=re.DOTALL)

path.write_text(content, encoding='utf-8')
print("Patched matcher.py")
