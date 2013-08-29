# TINY.ASM

My submission for http://redd.it/1kqxz9:

> Tiny, a very simple fictional computer architecture, is programmed by an assembly language that has 16 mnemonics, with 37 unique op-codes. The system is based on Harvard architecture, and is very straight-forward: program memory is different from working memory, the machine only executes one instruction at a time, memory is an array of bytes from index 0 to index 255 (inclusive), and doesn't have any relative addressing modes.
>
Your goal will be to write an assembler for Tiny: though you don't need to simulate the code or machine components, you must take given assembly-language source code and produce a list of hex op-codes. You are essentially writing code that converts the lowest human-readable language to machine-readable language!

## Usage
- **Convert an .asm file to the official syntax (see [here](http://redd.it/1kqxz9))**: `python assembler.py --pp-only <filename>`
- **Parse an .asm file to hex code**: `python assembler.py <filename>`
- **Run an .asm file in the virtual machine**: `python virtualmachine.py <filename>`

## About `pi.asm`

`pi.asm` computes the value of π using a stochastic algorithm:

> Another Monte Carlo method for computing π is to draw a circle inscribed in a square, and randomly place dots in the square. The ratio of dots inside the circle to the total number of dots will approximately equal π/4. <small>From [Wikipedia](http://en.wikipedia.org/wiki/Pi#Geometry_and_trigonometry)</small>

Because of the random values and the word size of 8 bit, the result will have a very low precision and vary between runs. In addition, due to the lack of float point arithmetics, `pi.asm` will only output the equation to get π (e.g. `78/100*4`). I'm still working on implementing 16bit float point arithmetics for Tiny, so `pi.asm` might output the actual result.

## Syntax Additions
**Comments**

    ; This is a comment

**Labels**

    label:
    JMP :label

**Constants**

    $mem_addr = [0]
    $some_const = 5

    MOV $mem_addr $some_const

**Includes**

    #include file_name.asm

**Char Constants**

    APRINT '!'  ; Prints: !
    APRINT '\n' ; Prints a newline

## LICENSE

The MIT License (MIT)

Copyright (c) 2013 Markus Siemens

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
