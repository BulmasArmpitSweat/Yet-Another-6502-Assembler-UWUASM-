def strip_value_literal(literal: str) -> str:
    value = literal
    first_two = value[:2].upper()  # First two characters (case-insensitive)
    last_char = value[-1].upper() # Last character (case-insensitive)

    if first_two == "0B" or first_two == "0X":
        return value[2:]
    if value[0] == '$':
        return value[1:]
    if last_char == 'H' or last_char == 'D':
        return value[:-1]
    return value

def evaluate_value_literal(literal: str) -> int:
    value = literal
    first_two = value[:2].upper()  # First two characters (case-insensitive)
    last_char = value[-1].upper() # Last character (case-insensitive)
    base: int = 0

    if first_two == "0B":
        base = 2
    elif first_two == "0X" or value[0] == '$' or last_char == 'H':
        base = 16
    elif last_char == 'D':
        base = 10
    else:
        return None
    return base

def convert_value_literal(literal: str, base: int) -> int:
    return int(literal, base=base)