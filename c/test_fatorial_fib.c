#include <assert.h>

#include "fatorial_fib.h"

int main(void) {
    assert(fatorial(0) == 1);
    assert(fatorial(1) == 1);
    assert(fatorial(5) == 120);
    assert(fatorial(10) == 3628800ULL);
    assert(fatorial(20) == 2432902008176640000ULL);
    assert(fatorial(21) == 0);
    assert(fatorial(-1) == 0);

    assert(fibonacci(0) == 0);
    assert(fibonacci(1) == 1);
    assert(fibonacci(2) == 1);
    assert(fibonacci(10) == 55);
    assert(fibonacci(50) == 12586269025ULL);
    assert(fibonacci(93) == 12200160415121876738ULL);
    assert(fibonacci(94) == 0);
    assert(fibonacci(-3) == 0);
    return 0;
}
