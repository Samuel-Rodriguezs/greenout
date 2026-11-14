#include <assert.h>
#include <stdio.h>
#include "mdc_modular.h"

int main(void) {
    assert(mdc(12, 18) == 6);
    assert(mdc(18, 12) == 6);
    assert(mdc(0, 5) == 5);
    assert(mdc(5, 0) == 5);
    assert(mdc(0, 0) == 0);
    assert(mdc(17, 13) == 1);
    assert(mdc(1000000007ULL * 3, 1000000007ULL * 5) == 1000000007ULL);
    assert(mmc(4, 6) == 12);
    assert(mmc(0, 6) == 0);
    assert(mmc(7, 7) == 7);

    assert(exp_mod(2, 10, 1000) == 24);
    assert(exp_mod(2, 0, 7) == 1);           /* x^0 = 1 */
    assert(exp_mod(0, 0, 7) == 1);
    assert(exp_mod(0, 5, 7) == 0);
    assert(exp_mod(5, 3, 1) == 0);           /* modulo 1 */
    assert(exp_mod(5, 3, 0) == 0);           /* modulo invalido */
    assert(exp_mod(3, 200, 13) == 9);        /* 3^3 = 1 (mod 13); 200 mod 3 = 2 */
    /* Fermat: a^(p-1) = 1 mod p, com p primo grande (precisa de 128 bits) */
    uint64_t p = 18446744073709551557ULL;    /* maior primo < 2^64 */
    assert(exp_mod(2, p - 1, p) == 1);
    assert(exp_mod(123456789, p - 1, p) == 1);
    assert(exp_mod(1000000007ULL, 5, 1000000007ULL) == 0);  /* base multipla do modulo */

    assert(inverso_mod(3, 11) == 4);         /* 3*4 = 12 = 1 mod 11 */
    assert(inverso_mod(10, 17) == 12);
    assert(inverso_mod(6, 9) == 0);          /* nao coprimos */
    assert(inverso_mod(0, 7) == 0);
    assert(inverso_mod(5, 1) == 0);          /* m < 2 */
    assert(inverso_mod(1, 2) == 1);
    uint64_t inv = inverso_mod(123456789, p);
    assert(inv != 0);
    unsigned __int128 prod = (unsigned __int128)123456789 * inv % p;
    assert(prod == 1);
    puts("mdc_modular ok");
    return 0;
}
