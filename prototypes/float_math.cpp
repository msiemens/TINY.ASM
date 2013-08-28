#include <iostream>
#include <bitset>
#include <string>
#include <cmath>
#include <cstdio>
using namespace std;

typedef unsigned short uint8;
const int bits = 16;
const int exponent_length = 5;
const int mantissa_length = 10;

unsigned int bs_1_l[bits];
const int bias = pow(2, exponent_length - 1) - 1;
const int exponent_mask = ((1 << 5) - 1) << mantissa_length;
const int mantissa_mask = (1 << mantissa_length) - 1;
const int hidden_bit = (1 << 11);

string ui2b(int i)
{
    bitset<bits> n (i);
    return "0b" + n.to_string();
}


uint8 get_exponent(uint8 v)
{
    unsigned int r = 0;

    //*
    while (v >>= 1)
    {
      r++;
    }
    // */

    return bias + r;
}


uint8 get_mantissa(uint8 v, uint8 exponent)
{
    // std::cout << "Calculating mantissa of " << ui2b(v) << std::endl;
    // Remove highest bit → hidden bit
    v &= ~(bs_1_l[exponent - bias]);
    // std::cout << "Removing highest bit:   " << ui2b(v) << std::endl;


    int iterations = mantissa_length - (exponent - bias);
    // std::cout << "Normalizing by shifting left by " << iterations <<  std::endl;
    for (int i = 0; i < iterations; ++i)
    {
        v <<= 1;
        // std::cout << "              " << ui2b(v) << std::endl;
    }
    for (int i = 0; i > iterations; --i)
    {
        v >>= 1;
        // std::cout << "              " << ui2b(v) << std::endl;
    }

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
    // std::cout << std::dec;
    // std::cout << "Input:    " << i << std::endl;
    // std::cout << "Input:    " << ui2b(i) << std::endl;
    // std::cout << std::endl;

    uint8 exponent = get_exponent(i);
    // std::cout << "Exponent: " << (int) exponent << " (- " << bias << ")" << std::endl;
    // std::cout << "Exponent: " << ui2b(exponent) << std::endl;
    // std::cout << std::endl;

    uint8 mantissa = get_mantissa(i, exponent);
    // std::cout << "Mantissa: " << (int) mantissa << std::endl;
    // std::cout << "Mantissa: " << ui2b(mantissa) << std::endl;
    // std::cout << std::endl;

    int ieee754 = composite_ieee754(exponent, mantissa);
    // std::cout << "IEEE754:  " << ui2b(ieee754) << std::endl;

    // std::cout << "Result: " << mantissa2dec(mantissa) << " * 2 ^ " << exponent - bias << std::endl;
    // printf( "        %f\n", ldexp(mantissa2dec(mantissa), exponent - bias));

    // std::cout << "-----------------------------------------------------" << std::endl;
    // std::cout << i << ": " << ui2b(ieee754) << " (0x" << std::hex << ieee754 << ")" << std::endl;
    // std::cout << "-----------------------------------------------------" << std::endl << std::endl << std::endl;
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


float float2int(int f) {
    int mantissa = f & ((1 << (mantissa_length)) - 1);
    // std::cout << "Mantissa: " << (int) mantissa << std::endl;
    // std::cout << "Mantissa: " << ui2b(mantissa) << std::endl;
    int exponent = f >> mantissa_length;
    // std::cout << "Exponent: " << (int) exponent << " (- " << bias << ")" << std::endl;
    // std::cout << "Exponent: " << ui2b(exponent) << std::endl;
    return ldexp(mantissa2dec(mantissa), exponent - bias);
}

int float_mul(int f1, int f2) {
    int res_exp = 0;
    int res_mant = 0;
    int result = 0;

    int exp1 = (f1 & exponent_mask) >> mantissa_length;
    int exp2 = (f2 & exponent_mask) >> mantissa_length;
    int mant1 = (f1 & mantissa_mask) | hidden_bit;
    int mant2 = (f2 & mantissa_mask) | hidden_bit;

    // cout << "exp1:  " << exp1 - bias << endl;
    // cout << "exp2:  " << exp2 - bias << endl;
    // cout << "mant1: " << ui2b(mant1) << endl;
    // cout << "mant2: " << ui2b(mant2) << endl;

    // Add exponents
    res_exp = exp1 + exp2 - bias;

    // Multiply significants
    res_mant = mant1 * mant2;   // 22 bit!
    res_mant >>= 11;            // Shift 22bit int right to fit into 10 bit
    res_mant &= ~hidden_bit;    // Remove hidden bit



    // cout << endl;
    // cout << "res_exp:  " << res_exp - bias << endl;
    // cout << "          " << ui2b(res_exp - bias) << endl;
    // cout << "res_mant: " << res_mant << endl;
    // cout << "          " << ui2b(res_mant) << endl;


    result = (res_exp << bits - exponent_length - 1) | res_mant;
    // cout << "res:      " << result << endl;
    // cout << "          0x" << hex << result << dec << endl;
    // cout << "          " << ui2b(result) << endl;

    cout << /* "Result:   " << */ float2int(result) << endl;
    // printf( "        %f\n", ldexp(int_to_decimals(res_mant), res_exp - bias));
}

int main(int argc, char const *argv[])
{

    for (int i = 0; i < bits; ++i)
    {
        bs_1_l[i] = pow(2, i);
    }

    int to = 10;
    int i = 8, j = 4;
    // for (int i = 1; i < to; ++i)
    // {
        for (int j = 1; j < to; ++j)
        {
            int f_i = int2ieee754(i);
            int f_j = int2ieee754(j);

            cout << i << " * " << j << " = ";
            float_mul(f_i, f_j);
        }
    // }
    return 0;
}