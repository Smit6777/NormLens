import re

path = 'app/services/extractor.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

analyze_old = """        results = []
        if not products:
            results.append({
                "product": None,
                "category": None,
                "parameters": parameters,
                "mandatory": mandatory,
                "form": forms_found[0] if forms_found else None,
                "material": materials_found[0] if materials_found else None
            })
        else:
            for canon, sector in products:
                results.append({
                    "product": canon,
                    "category": sector,
                    "parameters": parameters,
                    "mandatory": mandatory,
                    "form": forms_found[0] if forms_found else None,
                    "material": materials_found[0] if materials_found else None
                })
        return results"""

analyze_new = """        results = []
        if not products:
            results.append({
                "product": None,
                "category": None,
                "parameters": parameters,
                "mandatory": mandatory,
                "form": forms_found[0] if forms_found else None,
                "material": materials_found[0] if materials_found else None
            })
        else:
            for canon, sector in products:
                # Localize form/material to this specific product to avoid cross-contamination
                # If the canonical product name contains a known form/material, use that!
                canon_l = canon.lower()
                c_form = next((f for f in forms_found if f in canon_l), None)
                if not c_form:
                    # Fallback to a form found near the product phrase, but for safety in multi-product, if there's multiple products, don't blindly assign the first form unless there's only 1 form.
                    c_form = forms_found[0] if len(forms_found) == 1 else None
                
                c_mat = next((m for m in materials_found if m in canon_l), None)
                if not c_mat:
                    c_mat = materials_found[0] if len(materials_found) == 1 else None

                results.append({
                    "product": canon,
                    "category": sector,
                    "parameters": parameters,
                    "mandatory": mandatory,
                    "form": c_form,
                    "material": c_mat
                })
        return results"""

text = text.replace(analyze_old, analyze_new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
