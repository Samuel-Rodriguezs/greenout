#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "bignum.h"

static void confere(char *r, const char *esperado) {
    assert(r != NULL);
    assert(strcmp(r, esperado) == 0);
    free(r);
}

int main(void) {
    /* soma */
    confere(big_soma("0", "0"), "0");
    confere(big_soma("999", "1"), "1000");           /* propagacao de carry */
    confere(big_soma("1", "999"), "1000");
    confere(big_soma("123", "0"), "123");
    confere(big_soma("007", "003"), "10");           /* zeros a esquerda */
    confere(big_soma("99999999999999999999", "1"), "100000000000000000000");
    confere(big_soma("123456789012345678901234567890", "987654321098765432109876543210"),
            "1111111110111111111011111111100");
    /* multiplicacao */
    confere(big_mul("0", "12345"), "0");
    confere(big_mul("12345", "0"), "0");
    confere(big_mul("1", "1"), "1");
    confere(big_mul("99", "99"), "9801");
    confere(big_mul("123456789", "987654321"), "121932631112635269");
    confere(big_mul("99999999999999999999", "99999999999999999999"),
            "9999999999999999999800000000000000000001");
    confere(big_mul("0012", "003"), "36");
    /* fatorial */
    confere(big_fatorial(0), "1");
    confere(big_fatorial(1), "1");
    confere(big_fatorial(5), "120");
    confere(big_fatorial(20), "2432902008176640000");
    confere(big_fatorial(25), "15511210043330985984000000");
    confere(big_fatorial(50), "30414093201713378043612608166064768844377641568960512000000000000");
    /* entradas invalidas */
    assert(big_soma("", "1") == NULL);
    assert(big_soma("12a", "1") == NULL);
    assert(big_soma("-1", "1") == NULL);
    assert(big_mul("1", "") == NULL);
    assert(big_mul(NULL, "1") == NULL);
    puts("bignum ok");
    return 0;
}
