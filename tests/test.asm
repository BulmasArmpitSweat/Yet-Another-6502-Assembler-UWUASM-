LDX #$01
STX $00

SEC
LDY #$07 // calculates 7th fibonacci number (13 = D in hex) (CHANGE HERE IF YOU WANT TO CALCULATE ANOTHER NUMBER)
TYA // transfer y register to accumulator
SBC #$03 // handles the algorithm iteration counting
TAY // transfer the accumulator to the y register

CLC // clean carry
LDA #$02 // a = 2
STA $01 // stores a

loop: LDX $01 // x = a
      ADC $00 // a += x
      STA $01 // stores a
      STX $00 // stores x
      DEY // y -= 1
      BNE loop