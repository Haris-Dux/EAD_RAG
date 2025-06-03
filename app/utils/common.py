import re

def normalizeString(s:str) -> str:
    text = re.sub(r'[^a-z0-9]', '', s.lower())
    return text