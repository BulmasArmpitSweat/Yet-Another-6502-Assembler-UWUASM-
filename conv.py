#!/bin/python
import re

# Input: C struct text
c_struct = ["""
{ "LAS",
        "\\"AND\\" memory with stack pointer",
        "M & SP -> A X SP",
        "Load",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This undocumented instruction performs a bit-by-bit \\"AND\\" operation of the stack pointer and memory and\n\
        stores the result back in the accumulator, the index register X and the stack pointer.\n\n\
        \
        The LAS instruction does not affect the carry or overflow flags. It sets N if the bit 7 of the result is on,\n\
        otherwise it is reset. If the result is zero, then the Z flag is set, otherwise it is reset.",
        1,
        {
            {Y_INDEXED_ABSOLUTE, 0xBB, 3, "4+p", true}
        }
    },""",
	"""{ "LAX",
        "Load accumulator and index register X from memory",
        "M -> A X",
        "Load",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The undocumented LAX instruction loads the accumulator and the index register X from memory.\n\n\
        \
        LAX does not affect the C or V flags; sets Z if the value loaded was zero, otherwise resets it; sets N if the\n\
        value loaded in bit 7 is a 1; otherwise N is reset, and affects only the X register.",
        7,
        {
            {IMMEDIATE                   , 0xAB, 2, 2, true},
            {ABSOLUTE                    , 0xAF, 3, 4, true},
            {Y_INDEXED_ABSOLUTE          , 0xBF, 3, "4+p", true},
            {ZERO_PAGE                   , 0xA7, 2, 3, true},
            {Y_INDEXED_ZERO_PAGE         , 0xB7, 2, 4, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xA3, 2, 6, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xB3, 2, "5+p", true}
        }
    },""",
	"""{ "LDA",
        "Load Accumulator from memory",
        "M -> A",
        "Load",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "When instruction LDA is executed by the microprocessor, data is transferred from memory to the\n\
        accumulator and stored in the accumulator.\n\n\
        \
        LDA affects the contents of the accumulator, does not affect the carry or overflow flags; sets the zero\n\
        flag if the accumulator is zero as a result of the LDA, otherwise resets the zero flag; sets the negative\n\
        flag if bit 7 of the accumulator is a 1, otherwise resets the negative flag.",
        8,
        {
            {IMMEDIATE                   , 0xA9, 2, 2, false},
            {ABSOLUTE                    , 0xAD, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0xBD, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0xB9, 3, "4+p", false},
            {ZERO_PAGE                   , 0xA5, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0xB5, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xA1, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xB1, 2, "5+p", false}
        }
    },""",
	"""{ "LDX",
        "Load index X register from memory",
        "M -> X",
        "Load",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "Load the index register X from memory\n\n\
        \
        LDX does not affect the C or V flags; sets Z if the value loaded was zero, otherwise resets it; sets N if\n\
        the value loaded in bit 7 is a 1; otherwise N is reset, and only affects the X register.",
        5,
        {
            {IMMEDIATE          , 0xA2, 2, 2, false},
            {ABSOLUTE           , 0xAE, 3, 4, false},
            {Y_INDEXED_ABSOLUTE , 0xBE, 3, "4+p", false},
            {ZERO_PAGE          , 0xA6, 2, 3, false},
            {Y_INDEXED_ZERO_PAGE, 0xB6, 2, 4, false}
        }
    },""",
	"""{ "LDY",
        "Load index Y register from memory",
        "M -> Y",
        "Load",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "Load the index register Y from memory\n\n\
        \
        LDX does not affect the C or V flags; sets Z if the value loaded was zero, otherwise resets it; sets N if\n\
        the value loaded in bit 7 is a 1; otherwise N is reset, and only affects the Y register.",
        5,
        {
            {IMMEDIATE          , 0xA0, 2, 2, false},
            {ABSOLUTE           , 0xAC, 3, 4, false},
            {Y_INDEXED_ABSOLUTE , 0xBC, 3, "4+p", false},
            {ZERO_PAGE          , 0xA4, 2, 3, false},
            {Y_INDEXED_ZERO_PAGE, 0xB4, 2, 4, false}
        }
    },""",
	"""{ "SAX",
        "Store accumulator \\"AND\\" index register X in memory",
        "A & X -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The undocumented SAX instruction performs a bit-by-bit AND operation of the value of the accumulator and\n\
        the value of the index register X and stores the result in memory.\n\n\
        \
        No flags or registers in the microprocessor are affected by the store operation.",
        4,
        {
            {ABSOLUTE                    , 0x8F, 3, 4, true},
            {ZERO_PAGE                   , 0x87, 2, 3, true},
            {Y_INDEXED_ZERO_PAGE         , 0x97, 2, 4, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x83, 2, 6, true}
        }
    },""",
	"""{ "SHA",
        "Store accumulator \\"AND\\" index register X \\"AND\\" value",
        "A & X & V -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The undocumented SHA instruction performs a bit-by-bit AND operation of the following three operands:\n\
        The first two are the accumulator and the index register X.\n\n\
        \
        The third operand depends on the addressing mode. In the zero page indirect Y-indexed case, the third\n\
        operand is the data in memory at the given zero page address (ignoring the addressing mode's Y offset)\n\
        plus 1. In the Y-indexed absolute case, it is the upper 8 bits of the given address (ignoring the addressing\n\
        mode's Y offset), plus 1.\n\n\
        \
        It then transfers the result to the addressed memory location.\n\n\
        \
        No flags or registers in the microprocessor are affected by the store operation.",
        2,
        {
            {Y_INDEXED_ABSOLUTE          , 0x9F, 3, 5, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x93, 2, 6, true}
        }
    },""",
	"""{ "SHX",
        "Store index register X \\"AND\\" value",
        "X & (H + 1) -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The undocumented SHX instruction performs a bit-by-bit AND operation of the index register X and the\n\
        upper 8 bits of the given address (ignoring the addressing mode's Y offset), plus 1. It then transfers the\n\
        result to the addressed memory location.\n\n\
        \
        No flags or registers in the microprocessor are affected by the store operation.",
        1,
        {
            {Y_INDEXED_ABSOLUTE, 0x9E, 3, 5, true}
        }
    },""",
	"""{ "SHY",
        "Store index register Y \\"AND\\" value",
        "Y & (H + 1) -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The undocumented SHY instruction performs a bit-by-bit AND operation of the index register Y and the\n\
        upper 8 bits of the given address (ignoring the addressing mode's X offset), plus 1. It then transfers the\n\
        result to the addressed memory location.\n\n\
        \
        No flags or registers in the microprocessor are affected by the store operation.",
        1,
        {
            {Y_INDEXED_ABSOLUTE, 0x9C, 3, 5, true}
        }
    },""",
	"""{ "STA",
        "Store accumulator in memory",
        "A -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "This instruction transfers the contents of the accumulator to memory\n\n\
        \
        This instruction affects none of the flags in the processor status register and does not affect the\n\
        accumulator.",
        7,
        {
            {ABSOLUTE                    , 0x8D, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0x9D, 3, 5, false},
            {Y_INDEXED_ABSOLUTE          , 0x99, 3, 5, false},
            {ZERO_PAGE                   , 0x85, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0x95, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x81, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x91, 2, 6, false}
        }
    },""",
	"""{ "STX",
        "Store index X register in memory",
        "X -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "This instruction transfers the contents of the X index register to memory\n\n\
        \
        This instruction affects none of the flags in the processor status register and does not affect the\n\
        accumulator.",
        3,
        {
            {ABSOLUTE           , 0x8E, 3, 4, false},
            {ZERO_PAGE          , 0x86, 2, 3, false},
            {Y_INDEXED_ZERO_PAGE, 0x96, 2, 4, false}
        }
    },""",
	"""{ "STY",
        "Store index X register in memory",
        "Y -> M",
        "Load",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "This instruction transfers the contents of the Y index register to memory\n\n\
        \
        This instruction affects none of the flags in the processor status register and does not affect the\n\
        accumulator.",
        3,
        {
            {ABSOLUTE           , 0x8C, 3, 4, false},
            {ZERO_PAGE          , 0x84, 2, 3, false},
            {Y_INDEXED_ZERO_PAGE, 0x94, 2, 4, false}
        }
    },""",
	"""{ "SHS",
        "Transfer Accumulator \\"AND\\" Index Register X to Stack Pointer then Store Stack Pointer \\"AND\\" Hi-Byte In Memory",
        "A & X -> SP, SP & (H + 1) -> M",
        "Trans",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The undocumented SHS instruction performs a bit-by-bit AND operation of the value of the accumulator and\n\
        the value of the index register X and stores the result in the stack pointer. It then performs a bit-by-bit AND\n\
        operation of the resulting stack pointer and the upper 8 bits of the given address (ignoring the addressing\n\
        mode's Y offset), plus 1, and transfers the result to the addressed memory location.\n\n\
        \
        No flags or registers in the microprocessor are affected by the store operation.",
        1,
        {
            {Y_INDEXED_ABSOLUTE, 0x9B, 3, 5, true}
        }
    },""",
	"""{ "TAX",
        "Transfer accumulator to index X",
        "A -> X",
        "Trans",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction takes the value from the accumulator and transfers or loads it into the index register X\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAX only affects the index register X, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the index register X has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the index register X is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0xAA, 1, 2, false}
        }
    },""",
	"""{ "TAY",
        "Transfer accumulator to index register Y",
        "A -> Y",
        "Trans",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction takes the value from the accumulator and transfers or loads it into the index register Y\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAY only affects the index register Y, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the index register Y has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the index register Y is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0xA8, 1, 2, false}
        }
    },""",
	"""{ "TSX",
        "Transfer stack pointer to index register X",
        "SP -> X",
        "Trans",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction takes the value from the stack pointer and transfers or loads it into the index register X\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAX only affects the index register X, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the index register X has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the index register X is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0xBA, 1, 2, false}
        }
    },""",
	"""{ "TXA",
        "Transfer index register X to accumulator",
        "X -> A",
        "Trans",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction takes the value from the index register X and transfers or loads it into the accumulator\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAX only affects the accumulator, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the accumulator has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the accumulator is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0x8A, 1, 2, false}
        }
    },""",
	"""{ "TXS",
        "Transfer index register X to stack pointer",
        "X -> A",
        "Trans",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction takes the value from the index register X and transfers or loads it into the stack pointer\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAX only affects the stack pointer, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the stack pointer has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the stack pointer is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0x9A, 1, 2, false}
        }
    },""",
	"""{ "TYA",
        "Transfer index register Y to accumulator",
        "Y -> A",
        "Trans",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction takes the value from the index register Y and transfers or loads it into the accumulator\n\
        without disturbing the contents of the accumulator.\n\n\
        \
        TAX only affects the accumulator, and does not affect the C or V flags. The N flag is set if the\n\
        resultant value in the accumulator has bit 7 on, otherwise it is reset. The Z flag is set if the contents\n\
        of the accumulator is 0 after the operation, otherwise it is reset.",
        1,
        {
            {IMPLIED, 0x98, 1, 2, false}
        }
    },""",
	"""{ "PHA",
        "Push accumulator on stack",
        "A|v ST, SP--",
        "Stack",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction transfers the current value of the accumulator to the next location on the stack,\n\
        automatically decrementing the stack pointer to point to the next vacant location.\n\n\
        \
        The PHA instruction only affects the stack pointer register which is decremented by 1 as a result of\n\
        the operation. It does not affect any flags.",
        1,
        {
            {IMPLIED, 0x48, 1, 3, false}
        }
    },""",
	"""{ "PHP",
        "Push processor status register on stack",
        "SP|v ST, SP--",
        "Stack",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction transfers the current value of the processor status register to the next location on the stack,\n\
        automatically decrementing the stack pointer to point to the next vacant location.\n\n\
        \
        The PHA instruction only affects the stack pointer register which is decremented by 1 as a result of\n\
        the operation. It does not affect any flags.",
        1,
        {
            {IMPLIED, 0x08, 1, 3, false}
        }
    },""",
	"""{ "PLA",
        "Pull accumulator from stack",
        "SP++, A|^ ST",
        "Stack",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction increments the stack pointer then pulls the top item\n\
        from the stack, and transfers it to the accumulator.\n\n\
        \
        The PLA instruction does not affect the C or V flags. It sets N if bit 7 in\n\
        the accumulator is on, otherwise resets it. It also sets the Z flag if\n\
        the accumulator is equal to 0, otherwise resets it. The PLA instruction changes the content\n\
        of the accumulator to the contents of the memory location at the stack register plus 1, and\n\
        also increments the stack register.",
        1,
        {
            {IMPLIED, 0x68, 1, 4, false}
        }
    },""",
	"""{ "PLP",
        "Pull processor status from stack",
        "SP++, SP|^ ST",
        "Stack",
        {
            AFFECTED,
            AFFECTED,
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This instruction increments the stack pointer then pulls the top item\n\
        from the stack, and transfers it to the processor status register.\n\n\
        \
        Because the instruction affects the processor status register, it\n\
        affects all of the processor flags, with the exception of the B\n\
        flag, which is never transferred over and is always reset.",
        1,
        {
            {IMPLIED, 0x28, 1, 4, false}
        }
    },""",
	"""{ "ASL",
        "Arithmetic shift left",
        "C <- /M7...M0/ <- 0",
        "Shift",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The shift left instruction shifts either the accumulator or the address memory location 1 bit to the left,\n\
        with the bit 0 always being set to 0 and the input bit 7 being stored in the carry flag. ASL either shifts\n\
        the accumulator left 1 bit or is a read/modify/write instruction that affects only memory.\n\n\
        \
        The instruction does not affect the overflow bit, sets N equal to the result bit 7 (bit 6 in the input), sets\n\
        Z flag if the result is equal to 0, otherwise resets Z and stores the input bit 7 in the carry flag.\n\n\
        \
        NOTE: Revision A -> C of the 6502 had a fault with the ROR instruction, where it behaved more like this\n\
        instruction. Revision D fixed the issue. (see: help ROR)",
        5,
        {
            {ACCUMULATOR        , 0x0A, 1, 2, false},
            {ABSOLUTE           , 0x0E, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0x1E, 3, 7, false},
            {ZERO_PAGE          , 0x06, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0x16, 2, 6, false}
        }
    },""",
	"""{ "LSR",
        "Logical shift right",
        "0 -> /M7...M0/ -> C",
        "Shift",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            RESET
        },
        "This instruction shifts either the accumulator or a specified memory location 1 bit to the right, with\n\
        the higher bit of the result always being set to 0, and the low bit which is shifted out of the field being\n\
        stored in the carry flag.\n\n\
        \
        The shift right instruction either affects the accumulator by shift­ing it right 1 or is a read/modify/write\n\
        instruction which changes a specified memory location but does not affect any internal registers. The\n\
        shift right does not affect the overflow flag. The N flag is always reset. The Z flag is set if the result of\n\
        the shift is 0 and reset otherwise. The carry is set equal to bit 0 of the input.",
        5,
        {
            {ACCUMULATOR        , 0x4A, 1, 2, false},
            {ABSOLUTE           , 0x4E, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0x5E, 3, 7, false},
            {ZERO_PAGE          , 0x46, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0x56, 2, 6, false}
        }
    },""",
	"""{ "ROL",
        "Rotate left",
        "C <- /M7...M0/ <- C",
        "Shift",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The rotate left instruction shifts either the accumulator or addressed memory left 1 bit, with the input\n\
        carry being stored in bit 0 and with the input bit 7 being stored in the carry flags.\n\n\
        \
        The ROL instruction either shifts the accumulator left 1 bit and stores the carry in accumulator bit 0 or\n\
        does not affect the internal registers at all. The ROL instruction sets carry equal to the input bit 7, sets\n\
        N equal to the input bit 6 , sets the Z flag if the result of the ro­ tate is 0, otherwise it resets Z and does\n\
        not affect the overflow flag at all.",
        5,
        {
            {ACCUMULATOR        , 0x2A, 1, 2, false},
            {ABSOLUTE           , 0x2E, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0x3E, 3, 7, false},
            {ZERO_PAGE          , 0x26, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0x36, 2, 6, false}
        }
    },""",
	"""{ "ROR",
        "Rotate right",
        "C -> /M7...M0/ -> C",
        "Shift",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The rotate right instruction shifts either the accumulator or addressed memory right 1 bit with bit 0 shifted\n\
        into the carry and carry shifted into bit 7.\n\n\
        \
        The ROR instruction either shifts the accumulator right 1 bit and stores the carry in accumulator bit 7 or\n\
        does not affect the internal registers at all. The ROR instruction sets carry equal to input bit 0, sets N equal\n\
        to the input carry and sets the Z flag if the result of the rotate is 0; otherwise it resets Z and does not affect\n\
        the overflow flag at all.\n\
        \
        (Available on Microprocessors after June, 1976)\n\
        NOTE: Compiling with the INCLUDE_ROR_BUG flag enabled will compile the CPU with the aforementioned bug enabled.\n\n\
        \
        For context, in early revisions of the MOS 6502 (revisions before June 1976) had a bug with this instruction. It\n\
        behaved more or less like the ASL instruction (see: help ASL). The bug was finally patched in the revision D of\n\
        the chip. (see https://www.pagetable.com/?p=406 for more info.)",
        5,
        {
            {ACCUMULATOR        , 0x6A, 1, 2, false},
            {ABSOLUTE           , 0x6E, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0x7E, 3, 7, false},
            {ZERO_PAGE          , 0x66, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0x76, 2, 6, false}
        }
    },""",
	"""{ "AND",
        "\\"AND\\" memory with accumulator",
        "A & M -> A",
        "Logic",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The AND instruction transfer the accumulator and memory to the adder which performs a bit-by-bit AND\n\
        operation and stores the result back in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the zero flag if the result in the accumulator is 0, otherwise\n\
        resets the zero flag; sets the negative flag if the result in the accumulator has bit 7 on, otherwise resets the\n\
        negative flag.",
        8,
        {
            {IMMEDIATE                   , 0x29, 2, 2, false},
            {ABSOLUTE                    , 0x2D, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0x3D, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0x39, 3, "4+p", false},
            {ZERO_PAGE                   , 0x25, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0x35, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x21, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x31, 2, "5+p", false}
        }
    },""",
	"""{ "BIT",
        "Test bits in memory with accumulator",
        "A & M, M7 -> N, M6 -> V",
        "Logic",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This instruction performs an AND between a memory location and the accumulator but does not store the\n\
        result of the AND into the accumulator.\n\n\
        \
        The bit instruction affects the N flag with N being set to the value of bit 7 of the memory being tested, the V\n\
        flag with V being set equal to bit 6 of the memory being tested and Z being set by the result of the AND\n\
        operation between the accumulator and the memory if the result is Zero, Z is reset otherwise. It does not\n\
        affect the accumulator.",
        2,
        {
            {ABSOLUTE , 0x2C, 3, 4, false},
            {ZERO_PAGE, 0x24, 2, 3, false}
        }
    },""",
	"""{ "EOR",
        "\\"Exclusive OR\\" memory with accumulator",
        "A ^ M -> A",
        "Logic",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The EOR instruction transfers the memory and the accumulator to the adder which performs a binary\n\
        \\"EXCLUSIVE OR\\" on a bit-by-bit basis and stores the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the zero flag if the result in the accumulator is 0, otherwise\n\
        resets the zero flag sets the negative flag if the result in the accumulator has bit 7 on, otherwise resets the\n\
        negative flag.",
        8,
        {
            {IMMEDIATE                   , 0x49, 2, 2, false},
            {ABSOLUTE                    , 0x4D, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0x5D, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0x59, 3, "4+p", false},
            {ZERO_PAGE                   , 0x45, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0x55, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x41, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x51, 2, "5+p", false}
        }
    },""",
	"""{ "ORA",
        "\\"OR\\" memory with accumulator",
        "A | M -> A",
        "Logic",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The ORA instruction transfers the memory and the accumulator to the adder which performs a binary \\"OR\\"\n\
        on a bit-by-bit basis and stores the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the zero flag if the result in the accumulator is 0, otherwise\n\
        resets the zero flag; sets the negative flag if the result in the accumulator has bit 7 on, otherwise resets the\n\
        negative flag.",
        8,
        {
            {IMMEDIATE                   , 0x09, 2, 2, false},
            {ABSOLUTE                    , 0x0D, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0x1D, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0x19, 3, "4+p", false},
            {ZERO_PAGE                   , 0x05, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0x15, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x01, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x11, 2, "5+p", false}
        }
    },""",
	"""{ "ADC",
        "Add memory to accumulator with carry",
        "A + M + C -> A, C",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This instruction adds the value of memory and carry from the previous operation to the value of the\n\
        accumulator and stores the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the carry flag when the sum of a binary add exceeds 255 or\n\
        when the sum of a decimal add exceeds 99, otherwise carry is reset. The overflow flag is set when the sign\n\
        or bit 7 is changed due to the result exceeding +127 or -128, otherwise overflow is reset. The negative flag\n\
        is set if the accumulator result contains bit 7 on, otherwise the negative flag is reset. The zero flag is set if\n\
        the accumulator result is 0, otherwise the zero flag is reset.\n\
        NOTE: In decimal mode, the N, V and Z flags are not consistent with the decimal result.",
        8,
        {
            {IMMEDIATE                   , 0x69, 2, 2, false},
            {ABSOLUTE                    , 0x6D, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0x7D, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0x79, 3, "4+p", false},
            {ZERO_PAGE                   , 0x65, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0x75, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x61, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x71, 2, "5+p", false}
        }
    },""",
	"""{ "ANC",
        "\\"AND\\" memory with accumulator then move negative flag to carry flag",
        "A & M -> A, N -> C",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The undocumented ANC instruction performs a bit-by-bit AND operation of the accumulator and memory\n\
        and stores the result back in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the zero flag if the result in the accumulator is 0, otherwise\n\
        resets the zero flag; sets the negative flag and the carry flag if the result in the accumulator has bit 7 on,\n\
        otherwise resets the negative flag and the carry flag.",
        2,
        {
            {IMMEDIATE, 0x0B, 2, 2, true},
            {IMMEDIATE, 0x2B, 2, 2, true}
        }
    },""",
	"""{ "ARR",
        "\\"AND\\" accumulator then rotate right",
        "(A & M) / 2 -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "The undocumented ARR instruction performs a bit-by-bit \\"AND\\" operation of the accumulator and memory,\n\
        then shifts the result right 1 bit with bit 0 shifted into the carry and carry shifted into bit 7. It then stores the\n\
        result back in the accumulator.\n\n\
        \
        If bit 7 of the result is on, then the N flag is set, otherwise it is reset. The instruction sets the Z flag if the\n\
        result is 0; otherwise it resets Z.\n\n\
        \
        The V and C flags depends on the Decimal Mode Flag:\n\n\
        \
        In decimal mode, the V flag is set if bit 6 is different than the original data's bit 6, otherwise the V flag is\n\
        reset. The C flag is set if (operand & 0xF0) + (operand & 0x10) is greater than 0x50, otherwise the C flag is\n\
        reset.\n\n\
        \
        In binary mode, the V flag is set if bit 6 of the result is different than bit 5 of the result, otherwise the V flag is\n\
        reset. The C flag is set if the result in the accumulator has bit 6 on, otherwise it is reset.",
        1,
        {
            {IMMEDIATE, 0x6B, 2, 2, true}
        }
    },""",
	"""{ "ASR",
        "\\"AND\\" then logical shift right",
        "(A & M) / 2 -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            RESET
        },
        "The undocumented ASR instruction performs a bit-by-bit AND operation of the accumulator and memory,\n\
        then shifts the accumulator 1 bit to the right, with the higher bit of the result always being set to 0, and the\n\
        low bit which is shifted out of the field being stored in the carry flag.\n\n\
        \
        This instruction affects the accumulator. It does not affect the overflow flag. The N flag is always reset. The\n\
        Z flag is set if the result of the shift is 0 and reset otherwise. The carry is set equal to bit 0 of the result of the\n\
        \\"AND\\" operation",
        1,
        {
            {IMMEDIATE, 0x4B, 2, 2, true}
        }
    },""",
	"""{ "CMP",
        "Compare memory and accumulator",
        "A - M",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction subtracts the contents of memory from the contents of the accumulator.\n\n\
        \
        The use of the CMP affects the following flags: Z flag is set on an equal comparison, reset otherwise; the N\n\n\
        flag is set or reset by the result bit 7, the carry flag is set when the value in memory is less than or equal to\n\
        the accumulator, reset when it is greater than the accumulator. The accumulator is not affected.",
        8,
        {
            {IMMEDIATE                   , 0xC9, 2, 2, false},
            {ABSOLUTE                    , 0xCD, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0xDD, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0xD9, 3, "4+p", false},
            {ZERO_PAGE                   , 0xC5, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0xD5, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xC1, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xD1, 2, "5+p", false}
        }
    },""",
	"""{ "CPX",
        "Compare index register X to memory",
        "X - M",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction subtracts the value of the addressed memory location from the content of index register X\n\
        using the adder but does not store the result; therefore, its only use is to set the N, Z and C flags to allow for\n\
        comparison between the index register X and the value in memory.\n\n\
        \
        The CPX instruction does not affect any register in the machine; it also does not affect the overflow flag. It\n\
        causes the carry to be set on if the absolute value of the index register X is equal to or greater than the data\n\
        from memory. If the value of the memory is greater than the content of the index register X, carry is reset. If\n\
        the results of the subtraction contain a bit 7, then the N flag is set, if not, it is reset. If the value in memory is\n\
        equal to the value in index register X, the Z flag is set, otherwise it is reset.",
        3,
        {
            {IMMEDIATE, 0xE0, 2, 2, false},
            {ABSOLUTE , 0xEC, 3, 4, false},
            {ZERO_PAGE, 0xE4, 2, 3, false}
        }
    },""",
	"""{ "CPY",
        "Compare index register Y to memory",
        "Y - M",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction performs a two's complement subtraction between the index register Y and the specified\n\
        memory location. The results of the subtraction are not stored anywhere. The instruction is strictly used to\n\
        set the flags\n\n\
        \
        CPY affects no registers in the microprocessor and also does not affect the overflow flag. If the value in the\n\
        index register Y is equal to or greater than the value in the memory, the carry flag will be set, otherwise it will\n\
        be cleared. If the results of the subtraction contain bit 7 on the N bit will be set, otherwise it will be cleared.\n\
        If the value in the index register Y and the value in the memory are equal, the zero flag will be set, otherwise\n\
        it will be cleared",
        3,
        {
            {IMMEDIATE, 0xC0, 2, 2, false},
            {ABSOLUTE , 0xCC, 3, 4, false},
            {ZERO_PAGE, 0xC4, 2, 3, false}
        }
    },""",
	"""{ "DCP",
        "Decrement memory by one then compare with accumulator",
        "M - 1 ->, A - M",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This undocumented instruction subtracts 1, in two's complement, from the contents of the addressed\n\
        memory location. It then subtracts the contents of memory from the contents of the accumulator.\n\n\
        \
        The DCP instruction does not affect any internal register in the microprocessor. It does not affect the\n\
        overflow flag. Z flag is set on an equal comparison, reset otherwise; the N flag is set or reset by the result bit\n\
        7, the carry flag is set when the result in memory is less than or equal to the accumulator, reset when it is\n\
        greater than the accumulator.",
        7,
        {
            {ABSOLUTE                    , 0xCF, 3, 6, true},
            {X_INDEXED_ABSOLUTE          , 0xDF, 3, 7, true},
            {Y_INDEXED_ABSOLUTE          , 0xDB, 3, 7, true},
            {ZERO_PAGE                   , 0xC7, 2, 5, true},
            {X_INDEXED_ZERO_PAGE         , 0xD7, 2, 6, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xC3, 2, 8, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xD3, 2, 8, true}
        }
    },""",
	"""{ "ISC",
        "Increment Memory By One then SBC then Subtract Memory from Accumulator with Borrow",
        "M + 1 -> M, A - M -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This undocumented instruction adds 1 to the contents of the addressed memory location. It then subtracts\n\
        the value of the result in memory and borrow from the value of the accumulator, using two's complement\n\
        arithmetic, and stores the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator. The carry flag is set if the result is greater than or equal to 0. The\n\
        carry flag is reset when the result is less than 0, indicating a borrow. The overflow flag is set when the result\n\
        exceeds +127 or -127, otherwise it is reset. The negative flag is set if the result in the accumulator has bit 7\n\
        on, otherwise it is reset. The Z flag is set if the result in the accumulator is 0, otherwise it is reset.",
        7,
        {
            {ABSOLUTE                    , 0xEF, 3, 6, true},
            {X_INDEXED_ABSOLUTE          , 0xFF, 3, 7, true},
            {Y_INDEXED_ABSOLUTE          , 0xFB, 3, 7, true},
            {ZERO_PAGE                   , 0xE7, 2, 5, true},
            {X_INDEXED_ZERO_PAGE         , 0xF7, 2, 6, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xE3, 2, 8, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xF3, 2, 8, true}
        }
    },""",
	"""{ "RLA",
        "Rotate left then \\"AND\\" with accumulator",
        "C <- /M7...M0/ <- C, A & M -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The undocumented RLA instruction shifts the addressed memory left 1 bit, with the input carry being stored\n\
        in bit 0 and with the input bit 7 being stored in the carry flags. It then performs a bit-by-bit AND operation of\n\
        the result and the value of the accumulator and stores the result back in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the zero flag if the result in the accumulator is 0, otherwise\n\
        resets the zero flag; sets the negative flag if the result in the accumulator has bit 7 on, otherwise resets the\n\
        negative flag.",
        7,
        {
            {ABSOLUTE                    , 0x2F, 3, 6, false},
            {X_INDEXED_ABSOLUTE          , 0x3F, 3, 7, false},
            {Y_INDEXED_ABSOLUTE          , 0x3B, 3, 7, false},
            {ZERO_PAGE                   , 0x27, 2, 5, false},
            {X_INDEXED_ZERO_PAGE         , 0x37, 2, 6, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x23, 2, 8, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x33, 2, 8, false}
        }
    },""",
	"""{ "RRA",
        "Rotate right then add memory with accumulator",
        "C -> /M7...M0/ -> C, A + M + C -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "The undocumented RRA instruction shifts the addressed memory right 1 bit with bit 0 shifted into the carry\n\
        and carry shifted into bit 7. It then adds the result and generated carry to the value of the accumulator and\n\
        stores the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator; sets the carry flag when the sum of a binary add exceeds 255 or\n\
        when the sum of a decimal add exceeds 99, otherwise carry is reset. The overflow flag is set when the sign\n\
        or bit 7 is changed due to the result exceeding +127 or -128, otherwise overflow is reset. The negative flag\n\
        is set if the accumulator result contains bit 7 on, otherwise the negative flag is reset. The zero flag is set if\n\
        the accumulator result is 0, otherwise the zero flag is reset.",
        7,
        {
            {ABSOLUTE                    , 0x6F, 3, 6, true},
            {X_INDEXED_ABSOLUTE          , 0x7F, 3, 7, true},
            {Y_INDEXED_ABSOLUTE          , 0x7B, 3, 7, true},
            {ZERO_PAGE                   , 0x67, 2, 5, true},
            {X_INDEXED_ZERO_PAGE         , 0x77, 2, 6, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x63, 2, 8, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x73, 2, 8, true}
        }
    },""",
	"""{ "SBC",
        "Subtract memory from accumulator with borrow",
        "A - M - ~C -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This instruction subtracts the value of memory and borrow from the value of the accumulator, using two's\n\
        complement arithmetic, and stores the result in the accumulator. Borrow is defined as the carry flag\n\
        complemented; therefore, a resultant carry flag indicates that a borrow has not occurred.\n\n\
        \
        This instruction affects the accumulator. The carry flag is set if the result is greater than or equal to 0. The\n\
        carry flag is reset when the result is less than 0, indicating a borrow. The overflow flag is set when the result\n\
        exceeds +127 or -127, otherwise it is reset. The negative flag is set if the result in the accumulator has bit 7\n\
        on, otherwise it is reset. The Z flag is set if the result in the accumulator is 0, otherwise it is reset.\n\
        NOTE: In decimal mode, the N, V and Z flags are not consistent with the decimal result.",
        9,
        {
            {IMMEDIATE                   , 0xE9, 2, 2, false},
            {IMMEDIATE                   , 0xEB, 2, 2, true},
            {ABSOLUTE                    , 0xED, 3, 4, false},
            {X_INDEXED_ABSOLUTE          , 0xFD, 3, "4+p", false},
            {Y_INDEXED_ABSOLUTE          , 0xF9, 3, "4+p", false},
            {ZERO_PAGE                   , 0xE5, 2, 3, false},
            {X_INDEXED_ZERO_PAGE         , 0xF5, 2, 4, false},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0xE1, 2, 6, false},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0xF1, 2, "5+p", false}
        }
    },""",
	"""{ "SBX",
        "Subtract memory from accumulator \\"AND\\" index register X",
        "(A & X) - M -> X",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This undocumented instruction performs a bit-by-bit \\"AND\\" of the value of the accumulator and the index\n\
        register X and subtracts the value of memory from this result, using two's complement arithmetic, and stores\n\
        the result in the index register X.\n\n\
        \
        This instruction affects the index register X. The carry flag is set if the result is greater than or equal to 0.\n\
        The carry flag is reset when the result is less than 0, indicating a borrow. The negative flag is set if the result\n\
        in index register X has bit 7 on, otherwise it is reset. The Z flag is set if the result in index register X is 0,\n\
        otherwise it is reset. The overflow flag not affected at all.",
        1,
        {
            {IMMEDIATE, 0xCB, 2, 2, true}
        }
    },""",
	"""{ "SLO",
        "Arithmetic shift left then \\"OR\\" memory with accumulator",
        "M * 2 -> M, A | M -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The undocumented SLO instruction shifts the address memory location 1 bit to the left, with the bit 0 always\n\
        being set to 0 and the bit 7 output always being contained in the carry flag. It then performs a bit-by-bit \\"OR\\"\n\
        operation on the result and the accumulator and stores the result in the accumulator.\n\n\
        \
        The negative flag is set if the accumulator result contains bit 7 on, otherwise the negative flag is reset. It sets\n\
        Z flag if the result is equal to 0, otherwise resets Z and stores the input bit 7 in the carry flag.",
        7,
        {
            {ABSOLUTE                    , 0x0F, 3, 6, true},
            {X_INDEXED_ABSOLUTE          , 0x1F, 3, 7, true},
            {Y_INDEXED_ABSOLUTE          , 0x1B, 3, 7, true},
            {ZERO_PAGE                   , 0x07, 2, 5, true},
            {X_INDEXED_ZERO_PAGE         , 0x17, 2, 6, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x03, 2, 8, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x13, 2, 8, true}
        }
    },""",
	"""{ "SRE",
        "Logical shift right then \\"Exclusive OR\\" memory with accumulator",
        "M / 2 -> M, A ^ M -> A",
        "Arith",
        {
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The undocumented SRE instruction shifts the specified memory location 1 bit to the right, with the higher bit\n\
        of the result always being set to 0, and the low bit which is shifted out of the field being stored in the carry\n\
        flag. It then performs a bit-by-bit \\"EXCLUSIVE OR\\" of the result and the value of the accumulator and stores\n\
        the result in the accumulator.\n\n\
        \
        This instruction affects the accumulator. It does not affect the overflow flag. The negative flag is set if the\n\
        accumulator result contains bit 7 on, otherwise the negative flag is reset. The Z flag is set if the result is 0\n\
        and reset otherwise. The carry is set equal to input bit 0.",
        7,
        {
            {ABSOLUTE                    , 0x0F, 3, 6, true},
            {X_INDEXED_ABSOLUTE          , 0x1F, 3, 7, true},
            {Y_INDEXED_ABSOLUTE          , 0x1B, 3, 7, true},
            {ZERO_PAGE                   , 0x07, 2, 5, true},
            {X_INDEXED_ZERO_PAGE         , 0x17, 2, 6, true},
            {X_INDEXED_ZERO_PAGE_INDIRECT, 0x03, 2, 8, true},
            {ZERO_PAGE_INDIRECT_Y_INDEXED, 0x13, 2, 8, true}
        }
    },""",
	"""{ "XXA",
        "Non-deterministic operation of accumulator, index register X, memory, and bus contents",
        "(A & Q) & X & M -> A",
        "Arith",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "The operation of the undocumented XAA instruction depends on the individual microprocessor. On most\n\
        machines, it performs a bit-by-bit AND operation of the following three operands: The first two are the index\n\
        register X and memory.\n\n\
        \
        The third operand is the result of a bit-by-bit AND operation of the accumulator and a magic component.\n\
        This magic component depends on the individual microprocessor and is usually one of $00, $EE, $EF, $FE\n\
        and $FF, and may be influenced by the RDY pin, leftover contents of the data bus, the temperature of the\n\
        microprocessor, the supplied voltage, and other factors.\n\n\
        \
        On some machines, additional bits of the result may be set or reset depending on non-deterministic factors.\n\n\
        \
        It then transfers the result to the accumulator.\n\n\
        \
        XAA does not affect the C or V flags; sets Z if the value loaded was zero, otherwise resets it; sets N if the\n\
        result in bit 7 is a 1; otherwise N is reset.",
        1,
        {
            {IMMEDIATE, 0x8B, 2, 2, true}
        }
    },""",
	"""{ "DEC",
        "Decrement memory by one",
        "M - 1 -> M",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction subtracts 1, in two's complement, from the contents of the addressed memory location.\n\n\
        \
        The decrement instruction does not affect any internal register in the microprocessor. It does not affect the\n\
        carry or overflow flags. If bit 7 is on as a result of the decrement, then the N flag is set, otherwise it is reset.\n\
        If the result of the decrement is 0, the Z flag is set, otherwise it is reset.",
        4,
        {
            {ABSOLUTE           , 0xCE, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0xDE, 3, 7, false},
            {ZERO_PAGE          , 0xC6, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0xD6, 2, 6, false}
        }
    },""",
	"""{ "DEX",
        "Decrement index register X by one",
        "X - 1 -> X",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction subtracts one from the current value of the index register X and stores the result in the index\n\
        register X\n\n\
        \
        DEX does not affect the carry or overflow flag, it sets the N flag if it has bit 7 on as a result of the decrement,\n\
        otherwise it resets the N flag; sets the Z flag if X is a 0 as a result of the decrement, otherwise it resets the Z\n\
        flag.",
        1,
        {
            {IMPLIED, 0xCA, 1, 2, false}
        }
    },""",
	"""{ "DEY",
        "Decrement index register Y by one",
        "Y - 1 -> Y",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction subtracts one from the current value in the index register Y and stores the result into the\n\
        index register Y. The result does not affect or consider carry so that the value in the index register Y is\n\
        decremented to 0 and then through 0 to FF.\n\n\
        \
        Decrement Y does not affect the carry or overflow flags; if the Y register contains bit 7 on as a result of the\n\
        decrement the N flag is set, otherwise the N flag is reset. If the Y register is 0 as a result of the decrement,\n\
        the Z flag is set otherwise the Z flag is reset. This instruction only affects the index register Y.",
        1,
        {
            {IMPLIED, 0x88, 1, 2, false}
        }
    },""",
	"""{ "INC",
        "Increment memory by one",
        "M + 1 -> M",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "This instruction adds 1 to the contents of the addressed memory location.\n\n\
        \
        The increment memory instruction does not affect any internal registers and does not affect the carry or\n\
        overflow flags. If bit 7 is on as the result of the increment,N is set, otherwise it is reset; if the increment\n\
        causes the result to become 0, the Z flag is set on, otherwise it is reset.",
        4,
        {
            {ABSOLUTE           , 0xEE, 3, 6, false},
            {X_INDEXED_ABSOLUTE , 0xFE, 3, 7, false},
            {ZERO_PAGE          , 0xE6, 2, 5, false},
            {X_INDEXED_ZERO_PAGE, 0xF6, 2, 6, false}
        }
    },""",
	"""{ "INX",
        "Increment index register X by one",
        "X + 1 -> X",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "Increment X adds 1 to the current value of the X register. This is an 8-bit increment which does not affect the\n\
        carry operation, therefore, if the value of X before the increment was FF, the resulting value is 00.\n\n\
        \
        INX does not affect the carry or overflow flags; it sets the N flag if the result of the increment has a one in bit\n\
        7, otherwise resets N; sets the Z flag if the result of the increment is 0, otherwise it resets the Z flag.\n\n\
        \
        INX does not affect any other register other than the X register.",
        1,
        {
            {IMPLIED, 0xE8, 1, 2, false}
        }
    },""",
	"""{ "INY",
        "Increment index register Y by one",
        "Y + 1 -> Y",
        "Inc",
        {
            NOT_AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED
        },
        "Increment Y increments or adds one to the current value in the Y register, storing the result in the Y register.\n\
        As in the case of INX the primary application is to step thru a set of values using the Y register.\n\n\
        \
        The INY does not affect the carry or overflow flags, sets the N flag if the result of the increment has a one in\n\
        bit 7, otherwise resets N, sets Z if as a result of the increment the Y register is zero otherwise resets the Z\n\
        flag.",
        1,
        {
            {IMPLIED, 0xC8, 1, 2, false}
        }
    },""",
	"""{ "BRK",
        "Software breakpoint command",
        "PC + 2|v ST, SP--, [FFFE] -> PCL, [FFFF] -> PCH",
        "Ctrl",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            INITIALIZED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "The break command causes the microprocessor to go through an interrupt sequence under program\n\
        control. This means that the program counter of the second byte after the BRK. is automatically stored on\n\
        the stack along with the processor status at the beginning of the break instruction. The microprocessor then\n\
        transfers control to the interrupt vector.\n\n\
        \
        Other than changing the program counter, the break instruction changes no values in either the registers or\n\
        the flags.",
        1,
        {
            {IMPLIED, 0x00, 1, 7, false}
        }
    },""",
	"""{ "JMP",
        "JMP indirect",
        "[PC + 1] -> PCL, [PC + 2] -> PCH",
        "Ctrl",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction establishes a new value for the program counter.\n\n\
        \
        It affects only the program counter in the microprocessor and affects no flags in the status register.",
        2,
        {
            {ABSOLUTE         , 0x4C, 3, 3, false},
            {ABSOLUTE_INDIRECT, 0x6C, 3, 5, false}
        }
    },""",
	"""{ "JSR",
        "Jump to subroutine",
        "PC + 2|v ST, SP--, [PC + 1] -> PCL, [PC + 2] -> PCH",
        "Ctrl",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction transfers control of the program counter to a subroutine location but leaves a return pointer\n\
        on the stack to allow the user to return to perform the next instruction in the main program after the\n\
        subroutine is complete. To accomplish this, JSR instruction stores the program counter address which\n\
        points to the last byte of the jump instruction onto the stack using the stack pointer. The stack byte contains\n\
        the program count high first, followed by program count low. The JSR then transfers the addresses following\n\
        the jump instruction to the program counter low and the program counter high, thereby directing the program\n\
        to begin at that new address.\n\n\
        \
        The JSR instruction affects no flags, causes the stack pointer to be decremented by 2 and substitutes new\n\
        values into the program counter low and the program counter high.",
        1,
        {
            {ABSOLUTE, 0x20, 3, 6, false}
        }
    },""",
	"""{ "RTI",
        "Return from interrupt",
        "SR|v ST, SP--, PC + 2|v ST, SP--,",
        "Ctrl",
        {
            AFFECTED,
            AFFECTED,
            AFFECTED,
            AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            AFFECTED,
            AFFECTED
        },
        "This instruction transfers from the stack into the microprocessor the processor status and the program\n\
        counter location for the instruction which was interrupted. By virtue of the interrupt having stored this data \n\
        before executing the instruction and the fact that the RTI reinitializes the microprocessor to the same state\n\
        as when it was interrupted, the combination of interrupt plus RTI allows truly reentrant coding.\n\n\
        \
        The RTI instruction reinitializes all flags to the position to the point they were at the time the interrupt was\n\
        taken and sets the program counter back to its pre-interrupt state. It affects no other registers in the\n\
        microprocessor.",
        1,
        {
            {IMPLIED, 0x40, 1, 6, false}
        }
    },""",
	"""{ "RTS",
        "Return from subroutine",
        "SR|v ST, SP--, PC + 1 -> PC",
        "Ctrl",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction loads the program count low and program count high from the stack into the program\n\
        counter and increments the program counter so that it points to the instruction following the JSR. The stack\n\
        pointer is adjusted by incrementing it twice.\n\n\
        \
        The RTS instruction does not affect any flags and affects only PCL and PCH.",
        1,
        {
            {IMPLIED, 0x60, 1, 6, false}
        }
    },""",
	"""{ "BCC",
        "Branch on carry clear",
        "Branch if C == 0",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction tests the state of the carry bit and takes a conditional branch if the carry bit is reset.\n\n\
        \
        It affects no flags or registers other than the program counter and then only if the C flag is not on.",
        1,
        {
            {RELATIVE, 0x90, 2, "2+t+p", false}
        }
    },""",
	"""{ "BCS",
        "Branch on carry set",
        "Branch if C == 1",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction takes the conditional branch if the carry flag is on.\n\n\
        \
        BCS does not affect any of the flags or registers except for the program counter and only then if the carry\n\
        flag is on.",
        1,
        {
            {RELATIVE, 0xB0, 2, "2+t+p", false}
        }
    },""",
	"""{ "BEQ",
        "Branch on result zero",
        "Branch if Z == 1",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction could also be called \\"Branch on Equal.\\"\n\n\
        \
        It takes a conditional branch whenever the Z flag is on or the previous result is equal to 0.\n\n\
        \
        BEQ does not affect any of the flags or registers other than the program counter and only then when the Z\n\
        flag is set.",
        1,
        {
            {RELATIVE, 0xF0, 2, "2+t+p", false}
        }
    },""",
	"""{ "BMI",
        "Branch on result minus",
        "Branch if N == 1",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction takes the conditional branch if the N bit is set.\n\n\
        \
        BMI does not affect any of the flags or any other part of the machine other than the program counter and\n\
        then only if the N bit is on.",
        1,
        {
            {RELATIVE, 0x30, 2, "2+t+p", false}
        }
    },""",
	"""{ "BNE",
        "Branch on result not zero",
        "Branch if Z == 0",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction could also be called \\"Branch on Not Equal.\\" It tests the Z flag and takes the conditional\n\
        branch if the Z flag is not on, indicating that the previous result was not zero.\n\n\
        \
        BNE does not affect any of the flags or registers other than the program counter and only then if the Z flag is\n\
        reset.",
        1,
        {
            {RELATIVE, 0xD0, 2, "2+t+p", false}
        }
    },""",
	"""{ "BPL",
        "Branch on result plus",
        "Branch if N == 0",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction is the complementary branch to branch on result minus. It is a conditional branch which\n\
        takes the branch when the N bit is reset (0). BPL is used to test if the previous result bit 7 was off (0) and\n\
        branch on result minus is used to determine if the previous result was minus or bit 7 was on (1).\n\n\
        \
        The instruction affects no flags or other registers other than the P counter and only affects the P counter\n\
        when the N bit is reset.",
        1,
        {
            {RELATIVE, 0x10, 2, "2+t+p", false}
        }
    },""",
	"""{ "BVC",
        "Branch on overflow clear",
        "Branch if V == 0",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction tests the status of the V flag and takes the conditional branch if the flag is not set.\n\n\
        \
        BVC does not affect any of the flags and registers other than the program counter and only when the\n\
        overflow flag is reset.",
        1,
        {
            {RELATIVE, 0x50, 2, "2+t+p", false}
        }
    },""",
	"""{ "BVS",
        "Branch on overflow set",
        "Branch if V == 1",
        "Bra",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction tests the V flag and takes the conditional branch if V is on.\n\n\
        \
        BVS does not affect any flags or registers other than the program, counter and only when the overflow flag\n\
        is set.",
        1,
        {
            {RELATIVE, 0x70, 2, "2+t+p", false}
        }
    },""",
	"""{ "CLC",
        "Clear carry flag",
        "0 -> C",
        "Flags",
        {
            RESET,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction initializes the carry flag to a 0. This operation should normally precede an ADC loop. It is\n\
        also useful when used with a R0L instruction to clear a bit in memory.\n\n\
        \
        This instruction affects no registers in the microprocessor and no flags other than the carry flag which is\n\
        reset.",
        1,
        {
            {IMPLIED, 0x18, 1, 2, false}
        }
    },""",
	"""{ "CLD",
        "Clear decimal mode flag",
        "0 -> D",
        "Flags",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            RESET,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction sets the decimal mode flag to a 0. This all subsequent ADC and SBC instructions to operate\n\
        as simple operations.\n\n\
        \
        CLD affects no registers in the microprocessor and no flags other than the decimal mode flag which is set to\n\
        a 0.",
        1,
        {
            {IMPLIED, 0xD8, 1, 2, false}
        }
    },""",
	"""{ "CLI",
        "Clear interrupt disable flag",
        "0 -> I",
        "Flags",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            RESET,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction initializes the interrupt disable to a 0. This allows the microprocessor to receive interrupts.\n\n\
        \
        It affects no registers in the microprocessor and no flags other than the interrupt disable which is cleared.",
        1,
        {
            {IMPLIED, 0x58, 1, 2, false}
        }
    },""",
	"""{ "CLV",
        "Clear overflow flag",
        "0 -> V",
        "Flags",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            RESET,
            NOT_AFFECTED
        },
        "This instruction clears the overflow flag to a 0. This command is used in conjunction with the set overflow\n\
        pin which can change the state of the overflow flag with an external signal.\n\n\
        \
        CLV affects no registers in the microprocessor and no flags other than the overflow flag which is set to a 0.",
        1,
        {
            {IMPLIED, 0x58, 1, 2, false}
        }
    },""",
	"""{ "SEC",
        "Set carry flag",
        "1 -> C",
        "Flags",
        {
            INITIALIZED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction initializes the carry flag to a 1. This operation should normally precede a SBC loop. It is also\n\
        useful when used with a ROL instruction to initialize a bit in memory to a 1.\n\n\
        \
        This instruction affects no registers in the microprocessor and no flags other than the carry flag which is set.",
        1,
        {
            {IMPLIED, 0x38, 1, 2, false}
        }
    },""",
	"""{ "SED",
        "Set decimal mode flag",
        "1 -> D",
        "Flags",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            INITIALIZED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction sets the decimal mode flag D to a 1. This makes all subsequent ADC and SBC instructions\n\
        operate as a decimal arithmetic operation.\n\n\
        \
        SED affects no registers in the microprocessor and no flags other than the decimal mode which is set to a 1.\n\
        NOTE: The value of this flag is indeterminate after a RESET",
        1,
        {
            {IMPLIED, 0xF8, 1, 2, false}
        }
    },""",
	"""{ "SEI",
        "Set interrupt disable flag",
        "1 -> I",
        "Flags",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            INITIALIZED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED
        },
        "This instruction initializes the interrupt disable to a 1. It is used to mask interrupt requests during system\n\
        reset operations and during interrupt commands.\n\n\
        \
        It affects no registers in the microprocessor and no flags other than the interrupt disable which is set.",
        1,
        {
            {IMPLIED, 0x78, 1, 2, false}
        }
    },""",
	"""{ "NOP",
        "No operation",
        "No operation",
        "Nop",
        {
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
            NOT_AFFECTED,
        },
        "The name says it all. This command does nothing but waste time for 2 instructions. Can be used to align commands\n\
        up to execute on a certain clock cycle, or to waste for the sake of it.\n\n\
        \
        Wasting time is fun!",
        28,
        {
            {IMPLIED            , 0x1A, 1, 2, true},
            {IMPLIED            , 0x3A, 1, 2, true},
            {IMPLIED            , 0x5A, 1, 2, true},
            {IMPLIED            , 0x7A, 1, 2, true},
            {IMPLIED            , 0xDA, 1, 2, true},
            {IMPLIED            , 0xEA, 1, 2, false},
            {IMPLIED            , 0xFA, 1, 2, true},
            {IMMEDIATE          , 0x80, 2, 2, true},
            {IMMEDIATE          , 0x82, 2, 2, true},
            {IMMEDIATE          , 0x89, 2, 2, true},
            {IMMEDIATE          , 0xC2, 2, 2, true},
            {IMMEDIATE          , 0xE2, 2, 2, true},
            {ABSOLUTE           , 0x0C, 3, 4, true},
            {X_INDEXED_ABSOLUTE , 0x1C, 3, "4+p", true},
            {X_INDEXED_ABSOLUTE , 0x3C, 3, "4+p", true},
            {X_INDEXED_ABSOLUTE , 0x5C, 3, "4+p", true},
            {X_INDEXED_ABSOLUTE , 0x7C, 3, "4+p", true},
            {X_INDEXED_ABSOLUTE , 0xDC, 3, "4+p", true},
            {X_INDEXED_ABSOLUTE , 0xFC, 3, "4+p", true},
            {ZERO_PAGE          , 0x04, 2, 3, true},
            {ZERO_PAGE          , 0x44, 2, 3, true},
            {ZERO_PAGE          , 0x64, 2, 3, true},
            {X_INDEXED_ZERO_PAGE, 0x14, 2, 4, true},
            {X_INDEXED_ZERO_PAGE, 0x34, 2, 4, true},
            {X_INDEXED_ZERO_PAGE, 0x54, 2, 4, true},
            {X_INDEXED_ZERO_PAGE, 0x74, 2, 4, true},
            {X_INDEXED_ZERO_PAGE, 0xD4, 2, 4, true},
            {X_INDEXED_ZERO_PAGE, 0xF4, 2, 4, true}
        }
    }
};
"""]

# Ruleset to transform the input
rules = [
    (r'^\s*\{\s*', 'HelpMessage(', re.MULTILINE),  # Replace outermost opening brace
    (r'\}\s*,?\s*$', ')', re.MULTILINE),  # Replace outermost closing brace
    (r'\{\s*([^{}]*)\s*\}', r'[\1]', re.DOTALL),  # Replace inner `{}` with `[]`
    (r'\b(NOT_AFFECTED|AFFECTED|RESET|INITIALIZED)\b', r'Flag.\1'),  # Enum conversion
    (r'\b(true|false)\b', lambda m: 'True' if m.group(0) == 'true' else 'False'),  # Boolean values
    (
        r'\[([\w_]+),\s*(0x[0-9A-Fa-f]+|\d+),\s*(\d+),\s*"([^"]+)",\s*(True|False)\]',
        r'AddrModeInfo(AddressingModes.\1, \2, \3, "\4", \5)'
    ),  # Nested AddrModeInfo
    (r'\[\s*AddrModeInfo(.+?)\s*\]', r'[AddrModeInfo\1]', re.DOTALL),  # Ensure AddrModeInfo list uses brackets
    # Final rule: Replace any remaining {} with []
    (r'\{|\}', lambda match: '[' if match.group(0) == '{' else ']'),  # Final rule to replace all remaining { with [ and } with ]
    (r'](?!,)', '],')
]

# Function to apply transformations
def apply_rules(input_text, rules):
    output = input_text
    for pattern, repl, *flags in rules:
        output = re.sub(pattern, repl, output, *flags)
    return output

f = open("output.txt", "w")

for struct in c_struct:
    output = apply_rules(struct, rules)
    print(output, file=f)
