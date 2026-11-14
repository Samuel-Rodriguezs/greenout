#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "fisher_yates.h"

int main(void) {
    /* valores conhecidos do xorshift32 com seed 1 */
    Xorshift g;
    xorshift_iniciar(&g, 1);
    assert(xorshift_proximo(&g) == 270369u);
    assert(xorshift_proximo(&g) == 67634689u);
    /* seed 0 vira constante e nunca trava em zero */
    xorshift_iniciar(&g, 0);
    for (int i = 0; i < 1000; i++) assert(xorshift_proximo(&g) != 0);

    /* limites do xorshift_ate */
    xorshift_iniciar(&g, 42);
    assert(xorshift_ate(&g, 0) == 0);
    assert(xorshift_ate(&g, 1) == 0);
    for (int i = 0; i < 1000; i++) assert(xorshift_ate(&g, 7) < 7);

    /* n = 0 e 1 nao mexem em nada */
    int um[] = {9};
    embaralhar(um, 1, &g);
    assert(um[0] == 9);
    embaralhar(NULL, 0, &g);

    /* e uma permutacao: mesmos elementos */
    int a[50], b[50], visto[50];
    for (int i = 0; i < 50; i++) a[i] = i;
    xorshift_iniciar(&g, 123);
    embaralhar(a, 50, &g);
    memset(visto, 0, sizeof visto);
    for (int i = 0; i < 50; i++) { assert(a[i] >= 0 && a[i] < 50); visto[a[i]]++; }
    for (int i = 0; i < 50; i++) assert(visto[i] == 1);
    int mudou = 0;
    for (int i = 0; i < 50; i++) if (a[i] != i) mudou = 1;
    assert(mudou);

    /* determinismo: mesma seed, mesmo resultado; seed diferente, outro */
    for (int i = 0; i < 50; i++) b[i] = i;
    xorshift_iniciar(&g, 123);
    embaralhar(b, 50, &g);
    assert(memcmp(a, b, sizeof a) == 0);
    for (int i = 0; i < 50; i++) b[i] = i;
    xorshift_iniciar(&g, 124);
    embaralhar(b, 50, &g);
    assert(memcmp(a, b, sizeof a) != 0);

    /* uniformidade grosseira: cada elemento aparece em cada posicao ~N/3 vezes */
    int cont[3][3];
    memset(cont, 0, sizeof cont);
    xorshift_iniciar(&g, 2024);
    for (int t = 0; t < 30000; t++) {
        int v[3] = {0, 1, 2};
        embaralhar(v, 3, &g);
        for (int p = 0; p < 3; p++) cont[p][v[p]]++;
    }
    for (int p = 0; p < 3; p++)
        for (int e = 0; e < 3; e++) assert(cont[p][e] > 9000 && cont[p][e] < 11000);
    puts("fisher_yates ok");
    return 0;
}
