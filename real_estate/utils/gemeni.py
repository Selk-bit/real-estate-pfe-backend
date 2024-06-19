import browser_cookie3
from urllib.parse import quote, unquote
import re
from django.apps import apps


def decode_unicode_escapes(s):
    """
    Decodes common Unicode escape sequences in a string to their corresponding characters.

    Args:
    - s (str): The input string containing Unicode escape sequences.

    Returns:
    - str: The decoded string with Unicode escape sequences replaced by their actual characters.
    """
    # Dictionary of common Unicode escape sequences and their corresponding characters
    s = s.replace('\\\\', '\\')
    unicode_escapes = {
        "\\u003d": "=",  # Equal sign
        "\\u003c": "<",  # Less-than sign
        "\\u003e": ">",  # Greater-than sign
        "\\u0026": "&",  # Ampersand
        "\\u0027": "'",  # Single quote
        "\\u0022": "\"",  # Double quote
        "\\u0028": "(",  # Open parenthesis
        "\\u0029": ")",  # Close parenthesis
        "\\u002c": ",",  # Comma
        "\\u003b": ";",  # Semicolon
        "\\u002f": "/",  # Forward slash
        "\\u005c": "\\",  # Backslash
        "\\u007b": "{",  # Open curly brace
        "\\u007d": "}",  # Close curly brace
        "\\u005b": "[",  # Open square bracket
        "\\u005d": "]",  # Close square bracket
        "\\u002e": ".",  # Period
        "\\u0020": " ",  # Space
        "\\u000a": "\n",  # New line
        "\\u000d": "\r",  # Carriage return
        "\\u0009": "\t",  # Horizontal tab
    }

    for escape_sequence, char in unicode_escapes.items():
        s = s.replace(escape_sequence, char)

    return s


def to_number(e):
    try:
        return int(e)
    except ValueError:
        return None


def get_cookie():
    cookies = browser_cookie3.chrome(domain_name='.google.com')
    cookie_1psidts = ""
    cookie_3psidts = ""
    cookie_1psidcc = ""
    cookie_3psidcc = ""
    for i in cookies:
        if i.name == '__Secure-1PSIDTS':
            cookie_1psidts = i.value
        if i.name == '__Secure-3PSIDTS':
            cookie_3psidts = i.value
        if i.name == '__Secure-3PSIDCC':
            cookie_3psidcc = i.value
        if i.name == '__Secure-1PSIDCC':
            cookie_1psidcc = i.value
    return cookie_1psidts, cookie_3psidts, cookie_1psidcc, cookie_3psidcc


def get_encoded_description(desc):
    encoded_description = quote(desc)
    encoded_payload = f"f.req=%5Bnull%2C%22%5B%5B%5C%22{encoded_description}%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22fr%5C%22%5D%2C%5B%5C%22%5C%22%2C%5C%22%5C%22%2C%5C%22%5C%22%5D%2C%5C%22!UFOlUwvNAAZfVbE0f1VC0mv8uxEpTgk7ADQBEArZ1P6ElXbEQ6D2-DOrIem0I5lRBpnm-DGPC93KhBnbyBBm2Za0zEG9CA92R_JaA-hCAgAAAQpSAAAAo2gBB34AOQws-wtvJfCJW4EfguSBDh6pJYIgeBHFfnzUKzLKZJj7m7Q1r-VpHtKjEdoVFHXiDMadyqiEsuzMrQoAFHJFhv3MMZngn7Nl8lC_R2d8aOtwmQKwyY_L-nkKRxcKkbOwWRx9vhGQfymbgnHzGPzdShCv6ZgrckhPdZHAVbKuNjMDT2togFZB40MT_38lDK2ZZNJPr3uRqmh-lj5L8x0CZyVCz63IcAhAIdkYyCevYmel19pkFd2Q84ix8dThLXOt5Fn_-BYzNDzMMCgVfMs5fNz_4GTaMhre7Mjdsgn6DTBrwgdLdJRqtAtoRhl-1Ru2yAf7Igp5qGVxFmRSiGljJ0Jy3pIkzIW0VGkm1dFTr5rnJcuvb7t5Xy3VS-HRoWGlHwhARyTkidZRnYdMz91Qf_yZYPpap2jAWw0DUyOxHn5qA63B7kF6K33-QlP9cUGk13pYllbE0rPreUOuV30p51PdBJvoJLCf05CJ1QVa_MhXt5AbXgmFKjDXsv_o3PdMequFKlm31HRmWW4ec1tgMUv_69Uc5JfqJXJqnbC-51Zw328B8Bz4V0De5__TO4-JrrUKb9fp0RPFktHKMDP9GmYlGnZz39jOkkQYAlx0ANiKlxTW09vcbmfEpn57R8Goa55gDqm5Ejuozxpp_LoQsrsGLgRQFADn02hNeyucUGKyUnqXOclONdeB33aRPVM3ocloT_9WlwU58yTOGLAzUFAf9oPAyk86gwDyB9-Yxwfb9felIeu4gZu78kzBmt4ijhjqT9WkQeTknB_6gxw2M3e7s2TjKGIGUrLcPz1iZRGr2HR_lk4F4vfPMcOqswSUmYBbtTldual4vh7e_he30i8ikdIRrp0EWdvwiVbJzmKNZYlvBA1JHq4hZYTIg0rhgT3EC8rCq-SHVlba6BgcwyyNPFdC5PIAL-sfLlqaEmfaWU2zgheG4nC4YvbpXD19JJtQyryzslwiKzao2XyMewEOraNcl_rx5ItyI3dGAuKaRuKp0TNufgOCSVfVsVt2QUJ_-w%5C%22%2C%5C%2271db344d5b6c5dc74a05a4e24fa4edbd%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AFQ3Xea_Hyhw04pWSznSTBaf0KlM:1718646909742"
    encoded_payload = encoded_payload.replace("%0A", "%5C%5Cn")
    encoded_payload = encoded_payload.replace("%28", "(")
    encoded_payload = encoded_payload.replace("%27", "'")
    encoded_payload = encoded_payload.replace("%29", ")")
    encoded_payload = encoded_payload.replace("0D%", "")
    encoded_payload = encoded_payload.replace("/", "%2F")
    encoded_payload = encoded_payload.replace("%20%20%20%20", "%C2%A0%C2%A0")
    encoded_payload = encoded_payload.replace("%22%5C%5Cn", "%5C%5C%5C%22%5C%5Cn")
    encoded_payload = re.sub(r'(?<!%5C)%22(?!%)', r'%5C%5C%5C%22', encoded_payload)
    return encoded_payload


def get_encoded_prompt(desc):
    encoded_description = quote(desc)
    encoded_payload = f"f.req=%5Bnull%2C%22%5B%5B%5C%22{encoded_description}%5C%22%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2C0%5D%2C%5B%5C%22fr%5C%22%5D%2C%5B%5C%22%5C%22%2C%5C%22%5C%22%2C%5C%22%5C%22%5D%2C%5C%22!UFOlUwvNAAZfVbE0f1VC0mv8uxEpTgk7ADQBEArZ1P6ElXbEQ6D2-DOrIem0I5lRBpnm-DGPC93KhBnbyBBm2Za0zEG9CA92R_JaA-hCAgAAAQpSAAAAo2gBB34AOQws-wtvJfCJW4EfguSBDh6pJYIgeBHFfnzUKzLKZJj7m7Q1r-VpHtKjEdoVFHXiDMadyqiEsuzMrQoAFHJFhv3MMZngn7Nl8lC_R2d8aOtwmQKwyY_L-nkKRxcKkbOwWRx9vhGQfymbgnHzGPzdShCv6ZgrckhPdZHAVbKuNjMDT2togFZB40MT_38lDK2ZZNJPr3uRqmh-lj5L8x0CZyVCz63IcAhAIdkYyCevYmel19pkFd2Q84ix8dThLXOt5Fn_-BYzNDzMMCgVfMs5fNz_4GTaMhre7Mjdsgn6DTBrwgdLdJRqtAtoRhl-1Ru2yAf7Igp5qGVxFmRSiGljJ0Jy3pIkzIW0VGkm1dFTr5rnJcuvb7t5Xy3VS-HRoWGlHwhARyTkidZRnYdMz91Qf_yZYPpap2jAWw0DUyOxHn5qA63B7kF6K33-QlP9cUGk13pYllbE0rPreUOuV30p51PdBJvoJLCf05CJ1QVa_MhXt5AbXgmFKjDXsv_o3PdMequFKlm31HRmWW4ec1tgMUv_69Uc5JfqJXJqnbC-51Zw328B8Bz4V0De5__TO4-JrrUKb9fp0RPFktHKMDP9GmYlGnZz39jOkkQYAlx0ANiKlxTW09vcbmfEpn57R8Goa55gDqm5Ejuozxpp_LoQsrsGLgRQFADn02hNeyucUGKyUnqXOclONdeB33aRPVM3ocloT_9WlwU58yTOGLAzUFAf9oPAyk86gwDyB9-Yxwfb9felIeu4gZu78kzBmt4ijhjqT9WkQeTknB_6gxw2M3e7s2TjKGIGUrLcPz1iZRGr2HR_lk4F4vfPMcOqswSUmYBbtTldual4vh7e_he30i8ikdIRrp0EWdvwiVbJzmKNZYlvBA1JHq4hZYTIg0rhgT3EC8rCq-SHVlba6BgcwyyNPFdC5PIAL-sfLlqaEmfaWU2zgheG4nC4YvbpXD19JJtQyryzslwiKzao2XyMewEOraNcl_rx5ItyI3dGAuKaRuKp0TNufgOCSVfVsVt2QUJ_-w%5C%22%2C%5C%2271db344d5b6c5dc74a05a4e24fa4edbd%5C%22%2Cnull%2C%5B0%5D%2C1%2Cnull%2Cnull%2C1%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5D%5D%22%5D&at=AFQ3XeZ5NSdf_EDFRICF_6rd_2yj%3A1718649738089&"
    encoded_payload = encoded_payload.replace("%0A", "%5C%5Cn")
    encoded_payload = encoded_payload.replace("%28", "(")
    encoded_payload = encoded_payload.replace("%27", "'")
    encoded_payload = encoded_payload.replace("%29", ")")
    encoded_payload = encoded_payload.replace("0D%", "")
    encoded_payload = encoded_payload.replace("/", "%2F")
    encoded_payload = encoded_payload.replace("%20%20%20%20", "%C2%A0%C2%A0")
    encoded_payload = encoded_payload.replace("%22%5C%5Cn", "%5C%5C%5C%22%5C%5Cn")
    encoded_payload = encoded_payload.replace("%22%20", "%5C%5C%5C%22%20")
    encoded_payload = encoded_payload.replace("%20%22", "%20%5C%5C%5C%22")
    encoded_payload = re.sub(r'(?<!%5C)%22(?!%)', r'%5C%5C%5C%22', encoded_payload)
    return encoded_payload


def is_select_query(sql):
    """
    Check if the SQL query is a SELECT query.
    This is a very basic check and might need to be extended based on actual SQL query complexity.
    """
    return re.match(r'^\s*SELECT\s+', sql, re.IGNORECASE) is not None


def get_table_name_from_select(sql):
    """
    Extract the table name from a SELECT query.
    This is a simplistic approach and might not work for complex queries.
    """
    match = re.search(r'FROM\s+([\w]+)', sql, re.IGNORECASE)
    return match.group(1) if match else None


def table_exists(table_name):
    """
    Check if a table (Django model) exists.
    """
    if not table_name:
        return False
    for model in apps.get_models():
        if model._meta.db_table == table_name:
            return True
    return False


