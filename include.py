from enum import Enum

# Make handling tuples easier when dealing with the result from evaluate_line().
TUPLE_MNEMONIC = 0
TUPLE_ADDR_MODE = 1
TUPLE_ARG = 2
TUPLE_ARGTYPE = 3

# Make handling the instruction table easier
TABLE_ADDR_MODE = 0
TABLE_BYTECODE = 1
TABLE_IS_DOCUMENTED = 2

def error(msg: str, code: int=1, crash: bool=False) -> None:
    print(f"[ERROR][-{code}]: {msg}")
    if (crash):
        exit(-code)

class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __str__(self):
        return f"Token: {self.type} ({self.value})"

class Addr_Modes(Enum):
    IMPLIED                      = 1
    ACCUMULATOR                  = 2
    IMMEDIATE                    = 3
    ABSOLUTE                     = 4
    X_INDEXED_ABSOLUTE           = 5
    Y_INDEXED_ABSOLUTE           = 6
    ABSOLUTE_INDIRECT            = 7
    ZERO_PAGE                    = 8
    X_INDEXED_ZERO_PAGE          = 9
    Y_INDEXED_ZERO_PAGE          = 10
    X_INDEXED_ZERO_PAGE_INDIRECT = 11
    ZERO_PAGE_INDIRECT_Y_INDEXED = 12
    ASSEMBLER_OPTION             = 13
    LABEL                        = 14
    JUMP_LABEL                   = 15

Addr_Modes_Strings = [
    "IMPLIED",
    "ACCUMULATOR",
    "IMMEDIATE",
    "ABSOLUTE",
    "X_INDEXED_ABSOLUTE",
    "Y_INDEXED_ABSOLUTE",
    "ABSOLUTE_INDIRECT",
    "ZERO_PAGE",
    "X_INDEXED_ZERO_PAGE",
    "Y_INDEXED_ZERO_PAGE",
    "X_INDEXED_ZERO_PAGE_INDIRECT",
    "ZERO_PAGE_INDIRECT_Y_INDEXED",
    "ASSEMBLER_OPTION",
    "LABEL",
    "JUMP_LABEL",
]

class TokenType:
    MNEMONIC                     = "MNEMONIC"
    LITERAL_8BIT                 = "LITERAL_8BIT"
    LITERAL_16BIT                = "LITERAL_16BIT"
    HASH                         = "HASH"
    OPENING_BRACKET              = "OPENING_BRACKET"
    CLOSING_BRACKET              = "CLOSING_BRACKET"
    COMMA                        = "COMMA"
    EQUALS                       = "EQUALS"
    ASSEMBLER_OPTION             = "ASSEMBLER_OPTION"
    OPT                          = "OPT"
    COLON                        = "COLON"
    UNKNOWN                      = "UNKNOWN"
    EOF                          = "EOF"

assembler_options = {
    "__NO-UNDOCUMENTED-INSTRUCTION-WARNING": False,
    "_KEEP_TEMPORARY_FILES": False,
}

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