#include <assert.h>
#include <stdio.h>
#include "crivo.h"

static int primo_ingenuo(size_t n) {
    if (n < 2) return 0;
    for (size_t d = 2; d * d <= n; d++) if (n % d == 0) return 0;
    return 1;
}

int main(void) {
    /* limites de borda: 0, 1, 2, 3 */
    for (size_t lim = 0; lim <= 3; lim++) {
        Crivo *c = crivo_criar(lim);
        assert(c);
        for (size_t n = 0; n <= lim + 3; n++)
            assert(crivo_eh_primo(c, n) == (n <= lim && primo_ingenuo(n)));
        crivo_liberar(c);
    }
    Crivo *c = crivo_criar(100);
    assert(c && crivo_contar(c) == 25);
    assert(crivo_eh_primo(c, 97) && !crivo_eh_primo(c, 91) && !crivo_eh_primo(c, 101));
    assert(!crivo_eh_primo(c, 0) && !crivo_eh_primo(c, 1) && crivo_eh_primo(c, 2));
    crivo_liberar(c);

    c = crivo_criar(1000000);
    assert(c && crivo_contar(c) == 78498);     /* pi(10^6) */
    assert(crivo_eh_primo(c, 999983) && !crivo_eh_primo(c, 999999));
    assert(!crivo_eh_primo(c, 1000001));       /* acima do limite */
    crivo_liberar(c);

    /* compara com teste ingenuo num limite que cruza fronteiras de 64 bits */
    c = crivo_criar(5000);
    assert(c);
    for (size_t n = 0; n <= 5000; n++) assert(crivo_eh_primo(c, n) == primo_ingenuo(n));
    crivo_liberar(c);
    crivo_liberar(NULL);                       /* liberar NULL e seguro */
    puts("crivo ok");
    return 0;
}
