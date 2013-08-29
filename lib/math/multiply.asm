; Define constants
    $math_mul_counter       = [_]


; SUBROUTINE: Multiply two integers
; ---------------------------------

;     Input: $arg1 & $arg2 as two integers
;    Output: $return's the multiplication of the two
; Algorithm: Sum arg1 arg0' times
math_multiply:
    MOV     $math_mul_counter   0       ; Reset variables
    MOV     $return             0

    math_mul_loop:
                                        ; counter == arg1 → break
    JEQ     :math_mul_done      $arg1   $math_mul_counter
    ADD     $math_mul_counter   1
    ADD     $return             $arg0
    JMP     :math_mul_loop              ; Loop iteration

    math_mul_done:
    JMP     $jump_back




; Alterntavie implementation: Using shift and add algorithm
; Progblem: Bit shifts are very slow, whereas TINY's addition is pertty fast
;           10*25 is ~100 ticks with the above algorithm, but >1000 with this one
; math_multiply:
;     MOV     $math_mul_counter   $math_mul_bits
;     MOV     $math_mul_return    0
;     MOV     $math_mul_arg0      $arg0
;     MOV     $math_mul_arg1      $arg1
;     MOV     $math_mul_jumpback  $jump_back
;
;     multiply_loop:
;     JEQ     :multiply_return    $math_mul_counter 0 ; counter == 0 → break
;
;     MOV     $math_mul_cmp       $math_mul_arg1
;     AND     $math_mul_cmp       1                   ; First bit set?
;     JEQ     :multiply_shift     $math_mul_cmp   0   ; cmp == 0 → skip
;     ADD     $math_mul_return    $math_mul_arg0      ; result += arg0
;
;     multiply_shift:
;     MOV     $jump_back          :multiply_jumpback1 ; arg0 <<= 1
;     MOV     $arg0               $math_mul_arg0
;     JMP     :binary_shift_left
;     multiply_jumpback1:
;     MOV     $math_mul_arg0      $return
;
;     MOV     $jump_back          :multiply_jumpback2 ; arg1 >>= 1
;     MOV     $arg0               $math_mul_arg1
;     JMP     :binary_shift_right
;     multiply_jumpback2:
;     MOV     $math_mul_arg1      $return
;
;     SUB     $math_mul_counter   1       ; counter--
;     JMP     :multiply_loop
;
;     multiply_return:
;     MOV     $return             $math_mul_return
;     JMP $math_mul_jumpback
;
;
; #include lib/binary/shift.asm