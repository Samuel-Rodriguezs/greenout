#include "fatorial_fib.h"

unsigned long long fatorial(int n) {
    if (n < 0 || n > 20) {
        return 0;
    }
    unsigned long long r = 1;
    for (int i = 2; i <= n; i++) {
        r *= (unsigned long long)i;
    }
    return r;
}

unsigned long long fibonacci(int n) {
    if (n < 0 || n > 93) {
        return 0;
    }
    unsigned long long a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        unsigned long long t = a + b;
        a = b;
        b = t;
    }
    return a;
}
