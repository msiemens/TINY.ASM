#include <iostream>
using namespace std;

int multiply(int arg0, int arg1) {
    int result = 0;      // Result
    int counter = 16;    // Number of bits

    while (counter > 0) {
        if (arg1 & 1)
        {
            result += arg0;
        }

        if (b & 0x100)
        {
            // Overflowing!
            cerr << "OVERFLOW!" << endl;
        }

        arg0 <<= 1;
        arg1 >>= 1;
        counter--;
    }

    return result;
}

int main(int argc, char const *argv[])
{
    cout << multiply(256, 256) << endl;
    return 0;
}