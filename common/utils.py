import json
import re

def readFile(file_name):
    s = ''
    with open(file_name, 'r') as file:
        s = file.read()
    return s

def quote_digits_and_blanks_if_needed(s):
    pattern = r'(?<!")([1-9*_])(?!")'
    def replace(match):
        return f'"{match.group(1)}"'
    return re.sub(pattern, replace, s.replace("'",'"'))

def extract_json_from_text_string(text_str: str,quote_digits=True):
    try:
        lp_idx = text_str.index('{')
        rp_idx = text_str.rindex('}')
        # Use quoteString to force the JSON to be correct (help the LLMs):
        json_str = text_str[lp_idx:rp_idx+1]
        if quote_digits:
            json_str = quote_digits_and_blanks_if_needed(json_str)
        json_obj = json.loads(json_str)
        return True, json_obj 
    except:
        return False, None
