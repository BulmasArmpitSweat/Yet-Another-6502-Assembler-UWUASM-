#!/bin/python
# Shebang to make running this easier
# Only works for UNIX kernels with the functionality available
# (for example, compiling the Linux kernel with the support enabled in the .config file)
import sys, re, unicodedata, struct, argparse
from typing import List, Tuple

from include import Token, Addr_Modes, TokenType, error, assembler_options
from include import TUPLE_MNEMONIC, TUPLE_ADDR_MODE, TUPLE_ARG, TUPLE_ARGTYPE
from include import TABLE_ADDR_MODE, TABLE_BYTECODE, TABLE_IS_DOCUMENTED
from include import Addr_Modes_Strings, addressing_modes
from tables import literal_position, size_in_bytes, arg_types, instruction_info

from value_literal import evaluate_value_literal, strip_value_literal, convert_value_literal

from regex import regex_init

from help_defs import HelpMessage, print_instruction_help
from help_instruction_table import instructions

argc = len(sys.argv)

def is_mnemonic(mnemonic: str, *matches: str) -> bool:
    for match in matches:
        if (mnemonic == match):
            return True
    return False

def clean_line(line: str) -> str:
    return ''.join(ch for ch in line if unicodedata.category(ch)[0] != "C" and ch != " ").upper()

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
command_line_options: argparse.ArgumentParser = argparse.ArgumentParser(prog="UWUASM v0.2", \
    description="Yet another assembler for the 6502", \
    usage="UWUASM v0.2 [-h] [input_file] [-o OUTPUT_FILE] [--verbose] [--help-instruction <INSTRUCTION>]")

# Add input file positional argument
command_line_options.add_argument("input_file", type=str, nargs="?", help="The input file to process. Omit this if using --help-instruction <INSTRUCTION>.")
# Optional output file
command_line_options.add_argument("-o", "--output-file", type=str, default=None, help="Specify the output file. Defaults to stdout if not provided.")
# Verbose flag
command_line_options.add_argument("--verbose", action="store_true", help="Enable verbose output.")
# Special --help <INSTRUCTION> handling
command_line_options.add_argument("--help-instruction", type=str, metavar="<INSTRUCTION>", help="Get detailed help for a specific instruction.")

args = command_line_options.parse_args()

if (args.help_instruction):
    for (idx, instruction) in enumerate(instructions):
        if (args.help_instruction.upper() == instruction.mnemonic):
            print_instruction_help(instruction)
            break
        else:
            continue
    else:
        error(f"[ERROR]: No information available for instruction '{args.help_instruction}'. Please check your spelling and try again", crash=True)
    exit(0)
    

in_file = None
out_file = None

regex: re = regex_init()

try:
    # Validate argument count
    if len(sys.argv) < 2:
        error("[ERROR]: No input file provided", crash=True)

    # Assign filenames and extra arguments
    in_filename = args.input_file
    out_filename = ""
    if (args.output_file == None):
        out_filename = "a.out"
    else:
        out_filename = args.output_file
    extra_args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    # Open files
    in_file = open(in_filename, 'r')
    out_file = open(out_filename, 'wb')

except FileNotFoundError as fnf_error:
    error(f"[ERROR]: File not found - {fnf_error}", crash=True)
except Exception as e:
    error(f"[EXCEPTION]: An unexpected error occurred - {e}", crash=True)

# Some lines with a label are started like this: "label: instruction". This should change that to "label:\ninstruction"
# JMP and JSR instructions can and will be sometimes passed a label. This inserts a separator to stop it appearing as a large mnemonic once whitespace is removed
buffer: str = in_file.read()
buffer = re.sub(r'(\w+:)(\s*[A-Za-z])', r'\1\n\2', buffer)
buffer = re.sub(r'\b(JMP|JSR|BCC|BCS|BEQ|BMI|BNE|BPL|BVC|BVS)\b\s*([A-Za-z0-9_]+)', r'\1, \2', buffer)

# Strips out comments and splits into distinct lines, ignoring empty lines
lines: List[str] = [line for line in re.sub(r'//[^\n]*|/\*.*?\*/', '', buffer, flags=re.DOTALL).splitlines() if line.strip()]

position: int = 0
labels: List[Tuple[str, int]] = []

for idx, line in enumerate(lines):

    # Tokenize, then convert line into an internal representation
    tokens: List[Token] = tokenize(clean_line(line), regex)
    line_representation: Tuple[str, Addr_Modes, str, int] = evaluate_line(tokens, idx + 1)

    # Handle assembler options
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.ASSEMBLER_OPTION):
        option: str = line_representation[TUPLE_ARG]
        try:
            assembler_options[option] = True
        except KeyError:
            print(f"[WARN]: Unknown assembler option '{option}'; Ignoring")
        finally:
            continue
    
    # Handle labels, appending them to the list of discovered labels
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.LABEL):
        labels.append((line_representation[TUPLE_ARG], position))
        continue
    
    # Handle jumps to a label, converting the label to an absolute memory address, and re-evaluating the line
    if (line_representation[TUPLE_ADDR_MODE] == Addr_Modes.JUMP_LABEL):
        for label in labels:
            if (line_representation[TUPLE_ARG] == label[0]):
                # Faking the tokens
                tokens = [Token(TokenType.MNEMONIC, line_representation[TUPLE_MNEMONIC]), Token(TokenType.LITERAL_16BIT, f"${format(label[1], '04X')}"), Token(TokenType.EOF, "EOF")]
                line_representation = evaluate_line(tokens, idx + 1)
    
    # Get index into the large instruction table
    table_index: int = 0
    for table_idx, addr_mode in enumerate(instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_ADDR_MODE]):
        if (line_representation[TUPLE_ADDR_MODE] == addr_mode):
            table_index = table_idx
            break
        else:
            continue
    else:
        error(f"[ERROR line: {idx + 1}]: Illegal Adressing Mode. Instruction'{line_representation[TUPLE_MNEMONIC]}' does not support the '{Addr_Modes_Strings[line_representation[TUPLE_ADDR_MODE].value - 1]}' addressing mode", crash=True)
    
    # Print a warning message if the instruction and/or addressing mode is undocumented
    if (instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_IS_DOCUMENTED][table_idx] == True and assembler_options.get("__NO-UNDOCUMENTED-INSTRUCTION-WARNING", True) == False):
        print(f"[WARN]: Instruction '{line_representation[TUPLE_MNEMONIC]}' with addr mode '{Addr_Modes_Strings[line_representation[TUPLE_ADDR_MODE].value - 1]}' Is undocumented and thus likely unstable. Use with caution.")
    
    # Write out the instruction bytecode to the output file
    try:
        out_file.write(struct.pack('<B', instruction_info[line_representation[TUPLE_MNEMONIC]][TABLE_BYTECODE][table_idx]))
    except Exception as e:
        error(f"[EXCEPTION]: An exception occurred when trying to write to the output file. Assembling cannot continue. Exception is as follows:\n{e}", crash=True)
    
    # Finally, write out the argument in little endian if one is passed
    mnemonic: str = line_representation[TUPLE_MNEMONIC]
    addr: Addr_Modes = line_representation[TUPLE_ADDR_MODE]
    arg: str = line_representation[TUPLE_ARG]
    argtype: int = line_representation[TUPLE_ARGTYPE]

    if (arg != ''):
        # Convert argument into an integer we can use
        value: int = convert_value_literal(strip_value_literal(arg), evaluate_value_literal(arg))
        # If instruction is a branch, calculate offset
        if (addr == Addr_Modes.ABSOLUTE and is_mnemonic(mnemonic, "BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS") == True):
            value = value - (position + 2)

            # Check that the offset isn't out of bounds
            if (value < -127 or value > 128):
                error(f"[ERROR line: {idx + 1}]: Branch target out of range")
            
            # Write out the offset
            out_file.write(struct.pack("<b", value))
            position += size_in_bytes[addr]
            continue

        # Change packing type based on the size of the argument passed
        if (argtype != 0):
            if (argtype == 8):
                out_file.write(struct.pack("<B", value))
            else:
                out_file.write(struct.pack("<H", value))
    # Update the position so that labels work
    position += size_in_bytes[addr]