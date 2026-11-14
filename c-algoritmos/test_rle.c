#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rle.h"

static void ida_e_volta(const uint8_t *dados, size_t n, size_t tam_codificado_esperado) {
    size_t cn = 0, dn = 0;
    uint8_t *c = rle_codificar(dados, n, &cn);
    assert(c);
    if (tam_codificado_esperado != (size_t)-1) assert(cn == tam_codificado_esperado);
    uint8_t *d = rle_decodificar(c, cn, &dn);
    assert(d && dn == n && (n == 0 || memcmp(d, dados, n) == 0));
    free(c);
    free(d);
}

int main(void) {
    ida_e_volta((const uint8_t *)"", 0, 0);                         /* vazio */
    ida_e_volta((const uint8_t *)"a", 1, 2);                        /* um byte */
    ida_e_volta((const uint8_t *)"aaabcc", 6, 6);                   /* 3a 1b 2c */
    ida_e_volta((const uint8_t *)"abcdef", 6, 12);                  /* pior caso: dobra */
    ida_e_volta((const uint8_t *)"11122", 5, 4);                    /* digitos nao confundem */
    uint8_t zeros[10] = {0};
    ida_e_volta(zeros, 10, 2);                                      /* byte 0 */
    uint8_t altos[] = {0xFF, 0xFF, 0x00, 0xFF};
    ida_e_volta(altos, 4, 6);

    /* corrida maior que 255 e dividida em varios pares */
    uint8_t *longa = malloc(600);
    assert(longa);
    memset(longa, 'x', 600);
    size_t cn;
    uint8_t *c = rle_codificar(longa, 600, &cn);
    assert(c && cn == 6);                       /* 255 + 255 + 90 */
    assert(c[0] == 255 && c[2] == 255 && c[4] == 90);
    free(c);
    ida_e_volta(longa, 600, 6);
    free(longa);

    /* conteudo exato */
    c = rle_codificar((const uint8_t *)"aaab", 4, &cn);
    assert(c && cn == 4 && c[0] == 3 && c[1] == 'a' && c[2] == 1 && c[3] == 'b');
    free(c);

    /* decodificacao invalida */
    size_t dn;
    uint8_t ruim_impar[] = {3, 'a', 2};
    assert(rle_decodificar(ruim_impar, 3, &dn) == NULL);
    uint8_t ruim_zero[] = {0, 'a'};
    assert(rle_decodificar(ruim_zero, 2, &dn) == NULL);
    puts("rle ok");
    return 0;
}
