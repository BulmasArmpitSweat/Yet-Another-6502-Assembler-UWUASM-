#!/bin/python
# Shebang to make running this easier
# Only works for UNIX kernels with the functionality available
# (for example, compiling the Linux kernel with the support enabled in the .config file)
import sys, re, unicodedata, struct
from typing import List, Tuple

from include import Token, Addr_Modes, TokenType, error, assembler_options
from include import TUPLE_MNEMONIC, TUPLE_ADDR_MODE, TUPLE_ARG, TUPLE_ARGTYPE
from include import TABLE_ADDR_MODE, TABLE_BYTECODE, TABLE_IS_DOCUMENTED
from include import Addr_Modes_Strings
import tables
argc = len(sys.argv)

token_patterns = [
        (TokenType.OPT, r"\bOPT\b"),                                                            # Used for defining assembler options in the file
        (TokenType.HASH, r"[#]"),                                                               # '#' that defines an immediate value
        (TokenType.LITERAL_16BIT, r"(0x[a-fA-F0-9]{4}|\$[a-fA-F0-9]{4}|0b[01]{16}|\d{1,5})"),   # 16 bit value literals
        (TokenType.LITERAL_8BIT, r"(0x[a-fA-F0-9]{2}|\$[a-fA-F0-9]{2}|0b[01]{8}|\d{1,3})"),     # 8 bit value literals
        (TokenType.MNEMONIC, r"[A-Za-z]+"),                                                     # Mnemonics are alphabetic sequences
        (TokenType.OPENING_BRACKET, r"[(]"),                                                    # '(' that starts an indirect memory location
        (TokenType.CLOSING_BRACKET, r"[)]"),                                                    # ')' that ends an indirect memory location
        (TokenType.COMMA, r"[,]"),                                                              # ',' that defines an offset using an index register (X,Y)
        (TokenType.EQUALS, r"[=]"),                                                             # Used for defining assembler options in the file
        (TokenType.COLON, r"[:]"),                                                              # Used for labels
        (TokenType.ASSEMBLER_OPTION, r"__[A-Za-z-]+"),                                          # Used for defining assembler options in the file
        (TokenType.UNKNOWN, r'.'),                                                              # Any unknown single character
]

# Addressing mode definitions
addressing_modes = {
    Addr_Modes.IMPLIED:                      [TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.ACCUMULATOR:                  [TokenType.MNEMONIC, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.IMMEDIATE:                    [TokenType.MNEMONIC, TokenType.HASH, TokenType.LITERAL_8BIT, TokenType.EOF],
    Addr_Modes.ABSOLUTE:                     [TokenType.MNEMONIC, TokenType.LITERAL_16BIT, TokenType.EOF],
    Addr_Modes.X_INDEXED_ABSOLUTE:           [TokenType.MNEMONIC, TokenType.LITERAL_16BIT, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.Y_INDEXED_ABSOLUTE:           [TokenType.MNEMONIC, TokenType.LITERAL_16BIT, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.ABSOLUTE_INDIRECT:            [TokenType.MNEMONIC, TokenType.OPENING_BRACKET, TokenType.LITERAL_16BIT, TokenType.CLOSING_BRACKET, TokenType.EOF],
    Addr_Modes.ZERO_PAGE:                    [TokenType.MNEMONIC, TokenType.LITERAL_8BIT, TokenType.EOF],
    Addr_Modes.X_INDEXED_ZERO_PAGE:          [TokenType.MNEMONIC, TokenType.LITERAL_8BIT, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.Y_INDEXED_ZERO_PAGE:          [TokenType.MNEMONIC, TokenType.LITERAL_8BIT, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.X_INDEXED_ZERO_PAGE_INDIRECT: [TokenType.MNEMONIC, TokenType.OPENING_BRACKET, TokenType.LITERAL_8BIT, TokenType.COMMA, TokenType.MNEMONIC, TokenType.CLOSING_BRACKET, TokenType.EOF],
    Addr_Modes.ZERO_PAGE_INDIRECT_Y_INDEXED: [TokenType.MNEMONIC, TokenType.OPENING_BRACKET, TokenType.LITERAL_8BIT, TokenType.CLOSING_BRACKET, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF],
    Addr_Modes.ASSEMBLER_OPTION:             [TokenType.HASH, TokenType.OPT, TokenType.EQUALS, TokenType.ASSEMBLER_OPTION, TokenType.EOF],
    Addr_Modes.LABEL:                        [TokenType.MNEMONIC, TokenType.COLON, TokenType.EOF],
    Addr_Modes.JUMP_LABEL:                   [TokenType.MNEMONIC, TokenType.COMMA, TokenType.MNEMONIC, TokenType.EOF]
    # The separator (TokenType.COMMA) is inserted before the file is split and cleaned up.
}

literal_position = {
    Addr_Modes.IMPLIED:                      0,
    Addr_Modes.ACCUMULATOR:                  0,
    Addr_Modes.IMMEDIATE:                    2,
    Addr_Modes.ABSOLUTE:                     1,
    Addr_Modes.X_INDEXED_ABSOLUTE:           1,
    Addr_Modes.Y_INDEXED_ABSOLUTE:           1,
    Addr_Modes.ABSOLUTE_INDIRECT:            2,
    Addr_Modes.ZERO_PAGE:                    1,
    Addr_Modes.X_INDEXED_ZERO_PAGE:          1,
    Addr_Modes.Y_INDEXED_ZERO_PAGE:          1,
    Addr_Modes.X_INDEXED_ZERO_PAGE_INDIRECT: 2,
    Addr_Modes.ZERO_PAGE_INDIRECT_Y_INDEXED: 2,
    Addr_Modes.ASSEMBLER_OPTION:             0,
    Addr_Modes.LABEL:                        0,
    Addr_Modes.JUMP_LABEL:                   0,
}

size_in_bytes = {
    Addr_Modes.IMPLIED:                      1,
    Addr_Modes.ACCUMULATOR:                  1,
    Addr_Modes.IMMEDIATE:                    2,
    Addr_Modes.ABSOLUTE:                     3,
    Addr_Modes.X_INDEXED_ABSOLUTE:           3,
    Addr_Modes.Y_INDEXED_ABSOLUTE:           3,
    Addr_Modes.ABSOLUTE_INDIRECT:            3,
    Addr_Modes.ZERO_PAGE:                    2,
    Addr_Modes.X_INDEXED_ZERO_PAGE:          2,
    Addr_Modes.Y_INDEXED_ZERO_PAGE:          2,
    Addr_Modes.X_INDEXED_ZERO_PAGE_INDIRECT: 2,
    Addr_Modes.ZERO_PAGE_INDIRECT_Y_INDEXED: 2,
    Addr_Modes.ASSEMBLER_OPTION:             0,
    Addr_Modes.LABEL:                        0,
    Addr_Modes.JUMP_LABEL:                   3,
}

arg_types = {
    Addr_Modes.IMPLIED:                      0,
    Addr_Modes.ACCUMULATOR:                  0,
    Addr_Modes.IMMEDIATE:                    8,
    Addr_Modes.ABSOLUTE:                     16,
    Addr_Modes.X_INDEXED_ABSOLUTE:           16,
    Addr_Modes.Y_INDEXED_ABSOLUTE:           16,
    Addr_Modes.ABSOLUTE_INDIRECT:            16,
    Addr_Modes.ZERO_PAGE:                    8,
    Addr_Modes.X_INDEXED_ZERO_PAGE:          8,
    Addr_Modes.Y_INDEXED_ZERO_PAGE:          8,
    Addr_Modes.X_INDEXED_ZERO_PAGE_INDIRECT: 8,
    Addr_Modes.ZERO_PAGE_INDIRECT_Y_INDEXED: 8,
    Addr_Modes.ASSEMBLER_OPTION:             0,
    Addr_Modes.LABEL:                        0,
    Addr_Modes.JUMP_LABEL:                   16,
}

def is_mnemonic(mnemonic: str, *matches: str) -> bool:
    for match in matches:
        if (mnemonic == match):
            return True
    return False

def r_init() -> re:
    return re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns))

def clean_line(line: str) -> str:
    return ''.join(ch for ch in line if unicodedata.category(ch)[0] != "C" and ch != " ").upper()

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

def tokenize(line: str, r: re) -> List[Token]:
    tokens: List[Token] = []
    # Scan the input line using the regexuwu
    for match in r.finditer(line):
        token_type = match.lastgroup
        value = match.group(token_type)
        tokens.append(Token(token_type, value))
    tokens.append(Token(TokenType.EOF, "EOF"))
    return tokens

def compile_token_types(tokens: Token) -> List[TokenType]:
    types: List[TokenType] = []
    for token in tokens:
        types.append(token.type)
    return types

# literal_position == list of positions of value literal for each addressing mode that will act as the instruction's arguments. 0 means the addressing mode doesn't have one
def evaluate_line(tokens: List[Token], linenum: int) -> Tuple[str, Addr_Modes, str, int]:
    for mode, pattern in addressing_modes.items():
        if (compile_token_types(tokens) == pattern):
            if (literal_position.get(mode, 0) != 0):
                # (mnemonic, addressing mode, value literal if exists, argument size (8 or 16))
                return (tokens[0].value, mode, tokens[literal_position.get(mode, 0)].value, arg_types[mode])
            else:
                if (mode == Addr_Modes.ASSEMBLER_OPTION):
                    return ("", mode, tokens[len(tokens) - 2].value, arg_types[mode])
                elif (mode == Addr_Modes.LABEL):
                    return ("", mode, tokens[0].value, arg_types[mode])
                elif (mode == Addr_Modes.JUMP_LABEL):
                    return (tokens[0].value, mode, tokens[2].value, arg_types[mode])
                else:
                    return (tokens[0].value, mode, "", arg_types[mode])
        else:
            continue
    error(f"[ERROR line: {linenum}]: Unknown addressing mode {' '.join(token.value for token in tokens)}", crash=True)

# --------------------------------------------------------------------------------------------------------------
# Program starts here
# --------------------------------------------------------------------------------------------------------------


# line = "lda #$ffff"
# line = clean_line(line)
# print(f"Original Line: {line}\nTokenized Line is as follows:")
# r = r_init()
# tokens = tokenize(line, r)
# for t in tokens:
#     print(f'    {t}')
# line_representation: Tuple[str, Addr_Modes, str] = evaluate_line(tokens, 0)
# print(line_representation)
# exit(0)

out_filename: str = ""
in_filename: str = ""
extra_args = []

if (argc == 1):
    error("[ERROR]: No input file provided", crash=True)
elif (argc == 2):
    in_filename = sys.argv[1]
    out_filename = "a.out"
elif (argc == 3):
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
else:
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
    extra_args = sys.argv[3:argc - 1]

try:
    in_file = open(in_filename, 'r')
    out_file = open(out_filename, 'wb')
except Exception as e:
    error(f"[EXCEPTION]: An exception occurred when trying to open a file. The exception is as follows: {e}", crash=True)

regex: re = r_init()

buffer: str = in_file.read()
# Some lines with a label are started like this: "label: instruction". This should change that to "label:\ninstruction"
buffer = re.sub(r'(\w+:)(\s*[A-Za-z])', r'\1\n\2', buffer)
# JMP and JSR instructions can and will be sometimes passed a label. This inserts a separator to stop it appearing as a large mnemonic once whitespace is removed
buffer = re.sub(r'\b(JMP|JSR|BCC|BCS|BEQ|BMI|BNE|BPL|BVC|BVS)\b\s*([A-Za-z0-9_]+)', r'\1, \2', buffer)
lines: List[str] = [line for line in re.sub(r'//[^\n]*|/\*.*?\*/', '', buffer, flags=re.DOTALL).splitlines() if line.strip()]

position: int = 0
labels: List[Tuple[str, int]] = []

for idx, line in enumerate(lines):
    tokens: List[Token] = tokenize(clean_line(line), regex)
    line_representation: Tuple[str, Addr_Modes, str, int] = evaluate_line(tokens, idx + 1)
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.ASSEMBLER_OPTION):
        try:
            assembler_options[line_representation[TUPLE_ARG]] = True
        except KeyError:
            print(f"[WARN]: Unknown assembler option '{line_representation[TUPLE_ARG]}'; Ignoring")
        finally:
            continue
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.LABEL):
        labels.append((line_representation[TUPLE_ARG], position))
        continue
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.JUMP_LABEL):
        for label in labels:
            if (line_representation[TUPLE_ARG] == label[0]):
                # Faking the tokens
                tokens = [Token(TokenType.MNEMONIC, line_representation[TUPLE_MNEMONIC]), Token(TokenType.LITERAL_16BIT, f"${format(label[1], '04X')}"), Token(TokenType.EOF, "EOF")]
                line_representation = evaluate_line(tokens, idx + 1)
    table: List[Addr_Modes] = tables.instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_ADDR_MODE]
    table_index: int = 0
    for table_idx, addr_mode in enumerate(table):
        if (line_representation[TUPLE_ADDR_MODE] != addr_mode):
            continue
        else:
            table_index = table_idx
            break
    else:
        error(f"[ERROR line: {idx + 1}]: Illegal Adressing Mode. Instruction'{line_representation[TUPLE_MNEMONIC]}' does not support the '{Addr_Modes_Strings[line_representation[TUPLE_ADDR_MODE].value - 1]}' addressing mode", crash=True)
    if (tables.instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_IS_DOCUMENTED][table_idx] == True and assembler_options.get("__NO-UNDOCUMENTED-INSTRUCTION-WARNING", True) == False):
        print(f"[WARN]: Instruction '{line_representation[TUPLE_MNEMONIC]}' with addr mode '{Addr_Modes_Strings[line_representation[TUPLE_ADDR_MODE].value - 1]}' Is undocumented and thus likely unstable. Use with caution.")
    try:
        out_file.write(struct.pack('<B', tables.instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_BYTECODE][table_idx]))
    except Exception as e:
        error(f"[EXCEPTION]: An exception occurred when trying to write to the output file. Assembling cannot continue. Exception is as follows:\n{e}", crash=True)
    if (line_representation[TUPLE_ARG] != ''):
        value: int = convert_value_literal(strip_value_literal(line_representation[TUPLE_ARG]), evaluate_value_literal(line_representation[TUPLE_ARG]))
        if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.ABSOLUTE and is_mnemonic(line_representation[TUPLE_MNEMONIC], "BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS") == True):
            offset = value - (position + 2)
            if (offset < -127 or value > 128):
                error(f"[ERROR line: {idx + 1}]: Branch target out of range")
            out_file.write(struct.pack("<b", offset))
            position += size_in_bytes[line_representation[TUPLE_ADDR_MODE]]
            continue
        if (line_representation[TUPLE_ARGTYPE] != 0):
            if (line_representation[TUPLE_ARGTYPE] == 8):
                out_file.write(struct.pack("<B", value))
            else:
                out_file.write(struct.pack("<H", value))
    position += size_in_bytes[line_representation[TUPLE_ADDR_MODE]]