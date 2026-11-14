#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "rng.h"

int main(void) {
    /* Determinismo: mesma semente, mesma sequencia. */
    Xorshift a, b;
    xs_seed(&a, 42); xs_seed(&b, 42);
    for (int i = 0; i < 100; i++) assert(xs_next(&a) == xs_next(&b));
    xs_seed(&b, 43);
    xs_seed(&a, 42);
    assert(xs_next(&a) != xs_next(&b));
    xs_seed(&a, 0);
    assert(xs_next(&a) != 0);

    /* Vetor de referencia oficial do PCG32 (seed 42, seq 54). */
    Pcg32 p;
    pcg_seed(&p, 42, 54);
    uint32_t esperado[] = {0xa15c02b7u, 0x7b47f409u, 0xba1d3330u,
                           0x83d2f293u, 0xbfa4784bu, 0xcbed606eu};
    for (int i = 0; i < 6; i++) assert(pcg_next(&p) == esperado[i]);

    /* Limites. */
    pcg_seed(&p, 1, 1);
    for (int i = 0; i < 10000; i++) {
        assert(pcg_limitado(&p, 7) < 7);
        double d = pcg_double(&p);
        assert(d >= 0.0 && d < 1.0);
    }

    /* Media ~0.5; qui-quadrado com 9 gl: 99,9% abaixo de 27.9. */
    pcg_seed(&p, 2024, 7);
    assert(fabs(rng_media(&p, 100000) - 0.5) < 0.01);
    double chi = rng_qui_quadrado(&p, 10, 100000);
    assert(chi >= 0 && chi < 27.9);
    puts("rng ok");
    return 0;
}
