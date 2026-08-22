import os
import json

TEMPLATES_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_templates():
    templates = []
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                templates.append(data)
    return templates

def match_template(text: str):
    import re
    templates = get_all_templates()
    
    # We only need to check the first few hundred characters or lines typically
    # But text contains the whole first page.
    for template in templates:
        pattern = template.get("regex_pattern")
        if pattern and re.search(pattern, text, re.IGNORECASE):
            return template
            
    return None
