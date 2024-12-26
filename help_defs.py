from enum import Enum
import locale
from typing import List, Tuple

class AddressingModes(Enum):
    IMPLIED = 0
    ACCUMULATOR = 1
    IMMEDIATE = 2
    ABSOLUTE = 3
    X_INDEXED_ABSOLUTE = 4
    Y_INDEXED_ABSOLUTE = 5
    ABSOLUTE_INDIRECT = 6
    ZERO_PAGE = 7
    X_INDEXED_ZERO_PAGE = 8
    Y_INDEXED_ZERO_PAGE = 9
    X_INDEXED_ZERO_PAGE_INDIRECT = 10
    ZERO_PAGE_INDIRECT_Y_INDEXED = 11
    NOTHING = 12

class Flag(Enum):
    AFFECTED = 0
    NOT_AFFECTED = 1
    RESET = 2
    INITIALIZED = 3

class HelpMessage:
    def __init__(self, mnemonic: str, operation_summary: str, operation_string: str, category: str, affected_flags: List[Flag], help_message: str, addr_mode_info_len: int, AddressingModes: Tuple[AddressingModes, int, int, str, bool]):
        self.mnemonic: str = mnemonic
        self.operation_summary: str = operation_summary
        self.operation_string: str = operation_string
        self.category: str = category
        self.affected_flags: List[Flag] = affected_flags
        self.help_message: str = help_message
        self.addr_mode_info_len: int = addr_mode_info_len
        self.AddressingModes: List[AddressingModes, int, int, str, bool] = AddressingModes

def print_instruction_help(instruction: HelpMessage) -> None:
    instruction.mnemonic = instruction.mnemonic.upper()
    print(f"Mnemonic: {instruction.mnemonic}")
    print(f"Summary: {instruction.operation_summary}")
    print(f"Category: {instruction.category}")
    print(f"Operation: {instruction.operation_string}")
    print("Affected flags:")
    print("| C | Z | I | D | B | _ | V | N |")
    print("|", end="")
    
    locale.setlocale(locale.LC_ALL, "")
    for flag in instruction.affected_flags:
        symbol = "✓" if flag == Flag.AFFECTED else \
                "-" if flag == Flag.NOT_AFFECTED else \
                "0" if flag == Flag.RESET else "1"
        print(f" {symbol} |", end="")
    print("\n")
    print("_" * 70 + "\n")
    print(f"\t{instruction.help_message}\n")
    print(f"Expected addressing modes: ({instruction.addr_mode_info_len} {'mode' if instruction.addr_mode_info_len == 1 else 'modes'})")
    
    for mode_info in instruction.AddressingModes[:instruction.addr_mode_info_len]:
        undoc_mark = '*' if mode_info[4] else ' '
        bytecode_hex = f"0x{mode_info[1]:02x}"
        
        if mode_info[0] == AddressingModes.IMPLIED:
            print(f"IMPLIED ({bytecode_hex}){undoc_mark}                      | {instruction.mnemonic}         | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.ACCUMULATOR:
            print(f"ACCUMULATOR ({bytecode_hex}){undoc_mark}                  | {instruction.mnemonic} A       | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.IMMEDIATE:
            print(f"IMMEDIATE ({bytecode_hex}){undoc_mark}                    | {instruction.mnemonic} #$HHLL  | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.ABSOLUTE:
            print(f"ABSOLUTE ({bytecode_hex}){undoc_mark}                     | {instruction.mnemonic} $HHLL   | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.X_INDEXED_ABSOLUTE:
            print(f"X INDEXED ABSOLUTE ({bytecode_hex}){undoc_mark}           | {instruction.mnemonic} $HHLL,X | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.Y_INDEXED_ABSOLUTE:
            print(f"Y INDEXED ABSOLUTE ({bytecode_hex}){undoc_mark}           | {instruction.mnemonic} $HHLL,Y | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.ABSOLUTE_INDIRECT:
            print(f"ABSOLUTE INDIRECT ({bytecode_hex}){undoc_mark}            | {instruction.mnemonic} ($HHLL) | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.ZERO_PAGE:
            print(f"ZERO PAGE ({bytecode_hex}){undoc_mark}                    | {instruction.mnemonic} $HH     | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.X_INDEXED_ZERO_PAGE:
            print(f"X INDEXED ZERO PAGE ({bytecode_hex}){undoc_mark}          | {instruction.mnemonic} $HH,X   | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.Y_INDEXED_ZERO_PAGE:
            print(f"Y INDEXED ZERO PAGE ({bytecode_hex}){undoc_mark}          | {instruction.mnemonic} $HH,X   | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.X_INDEXED_ZERO_PAGE_INDIRECT:
            print(f"X INDEXED ZERO PAGE INDIRECT ({bytecode_hex}){undoc_mark} | {instruction.mnemonic} ($HH,X) | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.ZERO_PAGE_INDIRECT_Y_INDEXED:
            print(f"ZERO PAGE INDIRECT Y INDEXED ({bytecode_hex}){undoc_mark} | {instruction.mnemonic} ($HH),Y | Number of Cycles: {mode_info[3]}")
        
        elif mode_info[0] == AddressingModes.NOTHING:
            print(f"NOTHING ({bytecode_hex}){undoc_mark}                      | {instruction.mnemonic} N/A     | Number of Cycles: {mode_info[3]}")
        print()
