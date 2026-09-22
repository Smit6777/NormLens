"""Export reports generation."""
import csv
import io
from app.models.schemas import AnalyzeResponse

def generate_csv_report(response: AnalyzeResponse) -> str:
    """Generate a CSV report from an AnalyzeResponse."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Requirement ID", 
        "Requirement Text", 
        "Recommended IS", 
        "Match Scores", 
        "Gaps Detected",
        "Suggested Fixes"
    ])
    
    # Write data
    for req in response.requirements:
        req_id = req.requirement_id
        text = req.raw_text
        
        recs = response.recommendations.get(req_id, [])
        rec_str = " | ".join([r.is_number for r in recs])
        score_str = " | ".join([str(round(r.system_match_score, 2)) for r in recs])
        
        gaps = [g.issue for g in response.gaps if req_id in g.requirement_ids]
        gap_str = " ; ".join(gaps)
        
        fixes = [f.suggested_revision for f in response.fix_suggestions if req_id in f.requirement_ids]
        fix_str = " ; ".join(fixes)
        
        writer.writerow([req_id, text, rec_str, score_str, gap_str, fix_str])
        
    return output.getvalue()
