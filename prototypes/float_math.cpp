#include <iostream>
#include <bitset>
#include <string>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using namespace std;

typedef unsigned int uint8;
const int bits = 16;
const int exponent_length = 5;
const int mantissa_length = 10;

const int bias = pow(2, exponent_length - 1) - 1;
const int exponent_mask = ((1 << exponent_length) - 1) << mantissa_length;
const int mantissa_mask = (1 << mantissa_length) - 1;
const int hidden_bit = (1 << 10);

string ui2b(int i)
{
    bitset<bits> n (i);
    return "0b" + n.to_string();
}


string ui2b_22(int i)
{
    bitset<22 + 1> n (i);
    return "0b" + n.to_string();
}

// ---------------------------------------------------------------------
// Int to float
// ---------------------------------------------------------------------

uint8 get_exponent(uint8 v)
{
    unsigned int r = 0;

    while (v >>= 1)
        {   r++;  }

    return bias + r;
}


uint8 get_mantissa(uint8 v, uint8 exponent)
{
    v &= ~(1 << exponent);
    int iterations = mantissa_length - (exponent - bias);
    for (int i = 0; i < iterations; ++i)
        {  v <<= 1;  }
    for (int i = 0; i > iterations; --i)
        {  v >>= 1;  }

    return v;
}

uint8 composite_ieee754(uint8 exponent, uint8 mantissa)
{
    uint8 ieee754 = 0;
    ieee754 |= (exponent << (bits - exponent_length - 1));
    ieee754 |= mantissa;

    return ieee754;
}


int int2ieee754(int i) {
    uint8 exponent = get_exponent(i);
    uint8 mantissa = get_mantissa(i, exponent);
    int ieee754 = composite_ieee754(exponent, mantissa);
    return ieee754;
}

float mantissa2dec(int mantissa) {
    float m = 1, h = 1;

    for (int i = 0; i < mantissa_length; ++i)
    {
        h *= 0.5;
        m += h * ((mantissa & (1 << (mantissa_length - 1))) != 0);
        mantissa <<= 1;
    }

    return m;
}

// ---------------------------------------------------------------------
// Float to int
// ---------------------------------------------------------------------

float float2int(int f) {
    int mantissa = f & ((1 << (mantissa_length)) - 1);
    int exponent = f >> mantissa_length;
    return ldexp(mantissa2dec(mantissa), exponent - bias);
}


uint8 highest_bit_pos(uint8 v) {
    register unsigned int r; // result of log2(v) will go here
    register unsigned int shift;

    r =     (v > 0xFFFF) << 4; v >>= r;
    shift = (v > 0xFF  ) << 3; v >>= shift; r |= shift;
    shift = (v > 0xF   ) << 2; v >>= shift; r |= shift;
    shift = (v > 0x3   ) << 1; v >>= shift; r |= shift;
                                            r |= (v >> 1);
    return r;
}

// ---------------------------------------------------------------------
// Multiplication of floats
// ---------------------------------------------------------------------

uint8 float_mul(uint8 f1, uint8 f2) {
    uint8 res_exp = 0;
    uint8 res_mant = 0;
    uint8 result = 0;

    uint8 exp1 = (f1 & exponent_mask) >> mantissa_length;
    uint8 exp2 = (f2 & exponent_mask) >> mantissa_length;
    uint8 mant1 = (f1 & mantissa_mask) | hidden_bit;
    uint8 mant2 = (f2 & mantissa_mask) | hidden_bit;

    // Add exponents
    res_exp = exp1 + exp2 - bias;

    // Multiply significants
    res_mant = mant1 * mant2;
    uint8 highest_bit = highest_bit_pos(res_mant);

    // Shift 22bit int right to fit into 10 bit
    if (highest_bit == 21) {
        res_exp += 1;
    }
    res_mant >>= highest_bit - 10;

    res_mant &= ~hidden_bit;    // Remove hidden bit

    result = (res_exp << mantissa_length) | res_mant;

    cout << " == " /* << "Result:   " << */;
    printf("%f", float2int(result));
    cout << endl;
    return result;
}

// ---------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------

int main(int argc, char const *argv[])
{
    if (argc == 3) {
        int arg1 = strtol(argv[1], NULL, 0);
        int arg2 = strtol(argv[2], NULL, 0);
        cout << arg1 << " * " << arg2; // << endl;
        float_mul(int2ieee754(arg1), int2ieee754(arg2));

        return 0;
    }

    int to = 4;
    //*
    for (int i = 1; i < to; ++i)
    {
    // */
        //*
        for (int j = 1; j < to; ++j)
        {
        // */
            cout << i << " * " << j; // << endl;
            float_mul(int2ieee754(i), int2ieee754(j));
            // cout << endl << endl;
        }
    }
    return 0;
}