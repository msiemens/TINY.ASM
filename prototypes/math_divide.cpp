#include <iostream>
using namespace std;

struct div_result {
    int quotient;
    int remainder;
};

div_result divide(int dividend, int divisor) {
    int quotient = 0;

    while (dividend >= divisor) {
        quotient += 1;
        dividend -= divisor;
    }

    div_result result = {quotient, dividend};
    return result;
}

int main(int argc, char const *argv[])
{
    div_result r;

    r = divide(256, 256);
    cout << r.quotient << ", R" << r.remainder << endl;

    r = divide(256, 3);
    cout << r.quotient << ", R" << r.remainder << endl;

    r = divide(5, 3);
    cout << r.quotient << ", R" << r.remainder << endl;

    r = divide(1, 3);
    cout << r.quotient << ", R" << r.remainder << endl;

    return 0;
}