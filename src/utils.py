import json

def sanitize_metadata(metadata_list):
    sanitized = []
    for md in metadata_list:
        clean = {}
        for k, v in md.items():
            if isinstance(v, list):
                clean[k] = json.dumps(v, ensure_ascii=False)
            else:
                clean[k] = v
        sanitized.append(clean)
    return sanitized
