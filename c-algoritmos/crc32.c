#include "crc32.h"

static uint32_t tabela[256];
static int tabela_pronta = 0;

static void montar_tabela(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        tabela[i] = c;
    }
    tabela_pronta = 1;
}

uint32_t crc32_atualizar(uint32_t crc, const uint8_t *dados, size_t n) {
    if (!tabela_pronta) montar_tabela();
    crc = ~crc;
    for (size_t i = 0; i < n; i++) crc = tabela[(crc ^ dados[i]) & 0xFF] ^ (crc >> 8);
    return ~crc;
}

uint32_t crc32_calcular(const uint8_t *dados, size_t n) {
    return crc32_atualizar(0, dados, n);
}
