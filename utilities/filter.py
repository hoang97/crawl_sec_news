import re

def match(document:str, keyword:str) -> bool:
    search = re.compile(f"{keyword}", flags=re.MULTILINE | re.IGNORECASE)
    result = search.search(document)
    return bool(result)

def match_short(document:str, short_keyword:str) -> bool:
    search = re.compile(f"(\W|^){short_keyword}(\W|$)", flags=re.MULTILINE | re.IGNORECASE)
    result = search.search(document)
    return bool(result)