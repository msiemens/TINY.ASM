#include <iostream>
#include <bitset>
#include <string>
#include <cmath>
#include <cstdio>
#include <cstdlib>

using namespace std;

typedef unsigned short uint8;
const int bits = 16;
const int exponent_length = 5;
const int mantissa_length = 10;
const int bias = pow(2, exponent_length - 1) - 1;


std::string ui2b(unsigned int uint8)
{
    std::bitset<bits> n (uint8);
    return "0b" + n.to_string();
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


int main(int argc, char const *argv[])
{
    if (argc == 2) {
        int to_convert = strtol(argv[1], NULL, 0);
        printf("%f\n", float2int(to_convert));
    }
    return 0;
}