#include <iostream>
#include <bitset>
#include <string>
#include <cmath>

typedef unsigned int uint;

// 32bit
/*
typedef unsigned int uint8;
const int bits = 32;
const int exponent_length = 8;
const int mantissa_length = 23;
// */

// 16bit
//*
typedef unsigned short uint8;
const int bits = 16;
const int exponent_length = 5;
const int mantissa_length = 10;
// */

const int bias = pow(2, exponent_length - 1) - 1;
unsigned int bs_1_l[bits];

std::string ui2b(unsigned int uint8)
{
    std::bitset<bits> n (uint8);
    return "0b" + n.to_string();
}


uint8 get_exponent(uint8 v)
{
    unsigned int r = 0;

    //*
    // WORKS ONLY WITH v <= 2**8 !!
    while (v != 0) {
        unsigned int _v = 0;

        if ((v & bs_1_l[1]) != 0) {
            _v += 1;
        }
        if ((v & bs_1_l[2]) != 0) {
             _v += 2;
        }
        if ((v & bs_1_l[3]) != 0) {
             _v += 4;
        }
        if ((v & bs_1_l[4]) != 0) {
             _v += 8;
        }
        if ((v & bs_1_l[5]) != 0) {
             _v += 16;
        }
        if ((v & bs_1_l[6]) != 0) {
             _v += 32;
        }
        if ((v & bs_1_l[7]) != 0) {
             _v += 64;
        }
        if ((v & bs_1_l[8]) != 0) {
             _v += 128;
        }
        v = _v;

        r++;
    };
    r--;
    // */

    /*
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


void int2ieee754(int i) {
    std::cout << std::dec;
    std::cout << "Input:    " << i << std::endl;
    // std::cout << "Input:    " << ui2b(i) << std::endl;
    // std::cout << std::endl;

    uint8 exponent = get_exponent(i);
    std::cout << "Exponent: " << (int) exponent << " (- " << bias << ")" << std::endl;
    // std::cout << "Exponent: " << ui2b(exponent) << std::endl;
    // std::cout << std::endl;

    uint8 mantissa = get_mantissa(i, exponent);
    std::cout << "Mantissa: " << (int) mantissa << std::endl;
    // std::cout << "Mantissa: " << ui2b(mantissa) << std::endl;
    // std::cout << std::endl;

    int ieee754 = composite_ieee754(exponent, mantissa);
    std::cout << "IEEE754:  " << ui2b(ieee754) << std::endl;

    // std::cout << "-----------------------------------------------------" << std::endl;
    // std::cout << i << ": " << ui2b(ieee754) << " (0x" << std::hex << ieee754 << ")" << std::endl;
    std::cout << "-----------------------------------------------------" << std::endl << std::endl << std::endl;
}


int main(int argc, char const *argv[])
{
    for (int i = 0; i < bits; ++i)
    {
        bs_1_l[i] = pow(2, i);
    }

    for (int i = 0; i <= 255; ++i)
    {
        int2ieee754(i);
    }

    return 0;
}