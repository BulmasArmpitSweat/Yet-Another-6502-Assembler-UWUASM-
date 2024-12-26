import re
from include import TokenType

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

def regex_init() -> re:
    return re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns))