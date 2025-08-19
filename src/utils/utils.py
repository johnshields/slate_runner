import random
import string


def generate_uid(prefix: str, length: int = 6) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"
