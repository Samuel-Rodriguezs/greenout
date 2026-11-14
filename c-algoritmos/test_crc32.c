#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "crc32.h"

int main(void) {
    const char *s = "123456789";
    assert(crc32_calcular((const uint8_t *)s, 9) == 0xCBF43926u);   /* valor de referencia */
    assert(crc32_calcular(NULL, 0) == 0);                           /* vazio */
    assert(crc32_calcular((const uint8_t *)"a", 1) == 0xE8B7BE43u);
    assert(crc32_calcular((const uint8_t *)"abc", 3) == 0x352441C2u);
    const char *frase = "The quick brown fox jumps over the lazy dog";
    assert(crc32_calcular((const uint8_t *)frase, strlen(frase)) == 0x414FA339u);

    /* incremental em qualquer ponto de corte == calculo de uma vez */
    size_t n = strlen(frase);
    uint32_t inteiro = crc32_calcular((const uint8_t *)frase, n);
    for (size_t corte = 0; corte <= n; corte++) {
        uint32_t c = crc32_atualizar(0, (const uint8_t *)frase, corte);
        c = crc32_atualizar(c, (const uint8_t *)frase + corte, n - corte);
        assert(c == inteiro);
    }
    uint8_t zeros[4] = {0, 0, 0, 0};
    assert(crc32_calcular(zeros, 4) == 0x2144DF1Cu);
    puts("crc32 ok");
    return 0;
}
