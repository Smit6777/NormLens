import json
from pathlib import Path
import sys

DATA_DIR = Path("data")

def load_json(filename):
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("Validating BIS Knowledge Base JSON files...")
    
    try:
        metadata = load_json("bis_metadata.json")
        compliance = load_json("bis_compliance.json")
        qco = load_json("qco_mapping.json")
        sources = load_json("sources.json")
        normative = load_json("normative_graph.json")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON Syntax Error: {e}")
        sys.exit(1)
        
    errors = 0
    warnings = 0
    
    # 1. Check Metadata
    is_numbers = set()
    for item in metadata:
        is_num = item.get("is_number")
        if not is_num:
            print(f"[ERROR] Missing is_number in metadata record")
            errors += 1
            continue
            
        if is_num in is_numbers:
            print(f"[ERROR] Duplicate IS number in metadata: {is_num}")
            errors += 1
        is_numbers.add(is_num)
        
        src_id = item.get("source_id")
        if not src_id:
            print(f"[ERROR] Missing source_id for {is_num} in metadata")
            errors += 1
        elif src_id not in sources:
            print(f"[ERROR] Unknown source_id '{src_id}' for {is_num} in metadata")
            errors += 1
            
    print(f"Validated {len(metadata)} metadata records.")

    # 2. Check Compliance
    for is_num, comp in compliance.items():
        if is_num not in is_numbers:
            print(f"[WARN] IS number '{is_num}' in compliance not found in metadata")
            warnings += 1
            
        src_id = comp.get("source_id")
        if src_id and src_id not in sources:
            print(f"[ERROR] Unknown source_id '{src_id}' for {is_num} in compliance")
            errors += 1
            
    print(f"Validated {len(compliance)} compliance records.")
    
    # 3. Check QCO
    for q in qco:
        is_num = q.get("is_number")
        if is_num not in is_numbers:
            print(f"[WARN] IS number '{is_num}' in QCO not found in metadata")
            warnings += 1
            
        src_id = q.get("source_id")
        if not src_id:
            print(f"[ERROR] Missing source_id in QCO for {is_num}")
            errors += 1
        elif src_id not in sources:
            print(f"[ERROR] Unknown source_id '{src_id}' in QCO for {is_num}")
            errors += 1
            
    print(f"Validated {len(qco)} QCO mapping records.")
    
    # 4. Check Normative
    for rel in normative:
        frm, to = rel.get("from_is"), rel.get("to_is")
        if not frm or not to:
            print(f"[ERROR] Invalid normative relationship: {rel}")
            errors += 1
            continue
            
        src_id = rel.get("source_id")
        if src_id and src_id not in sources:
            print(f"[ERROR] Unknown source_id '{src_id}' in normative for {frm}->{to}")
            errors += 1
            
    print(f"Validated {len(normative)} normative relationship records.")
    
    # Summary
    print("-" * 50)
    print(f"Validation complete. Errors: {errors}, Warnings: {warnings}")
    if errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
