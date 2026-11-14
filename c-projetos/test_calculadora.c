#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "calculadora.h"

static double v(const char *e) {
    double r;
    assert(calcular(e, &r) == 0);
    return r;
}

int main(void) {
    assert(v("1 + 2 * 3") == 7);
    assert(v("(1 + 2) * 3") == 9);
    assert(v("2 ^ 3 ^ 2") == 512);
    assert(v("10 - 4 - 3") == 3);
    assert(v("-3 + 5") == 2);
    assert(v("2 * -3") == -6);
    assert(fabs(v("7 / 2") - 3.5) < 1e-12);
    assert(v("-(2 + 3) * 2") == -10);
    double r;
    assert(calcular("1 / 0", &r) == -1);
    assert(calcular("(1 + 2", &r) == -1);
    assert(calcular("1 + ", &r) == -1);
    assert(calcular("1 2", &r) == -1);
    assert(calcular("", &r) == -1);
    puts("calculadora ok");
    return 0;
}
