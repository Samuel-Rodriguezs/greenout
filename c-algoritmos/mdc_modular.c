#include "mdc_modular.h"

uint64_t mdc(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = a % b; a = b; b = t; }
    return a;
}

uint64_t mmc(uint64_t a, uint64_t b) {
    if (a == 0 || b == 0) return 0;
    return a / mdc(a, b) * b;
}

uint64_t exp_mod(uint64_t base, uint64_t exp, uint64_t m) {
    if (m == 0) return 0;
    unsigned __int128 r = 1 % m, b = base % m;
    while (exp) {
        if (exp & 1) r = r * b % m;
        b = b * b % m;
        exp >>= 1;
    }
    return (uint64_t)r;
}

uint64_t inverso_mod(uint64_t a, uint64_t m) {
    if (m < 2) return 0;
    /* Euclides estendido com inteiros de 128 bits com sinal */
    __int128 r0 = (__int128)m, r1 = (__int128)(a % m);
    __int128 t0 = 0, t1 = 1;
    while (r1 != 0) {
        __int128 q = r0 / r1, tmp;
        tmp = r0 - q * r1; r0 = r1; r1 = tmp;
        tmp = t0 - q * t1; t0 = t1; t1 = tmp;
    }
    if (r0 != 1) return 0;
    if (t0 < 0) t0 += (__int128)m;
    return (uint64_t)t0;
}
