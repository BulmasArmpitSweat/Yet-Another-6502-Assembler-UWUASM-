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
}