#ifndef CRC32_H
#define CRC32_H
#include <stddef.h>
#include <stdint.h>

/* CRC-32 (IEEE 802.3, polinomio refletido 0xEDB88320, o mesmo do zlib/gzip). */
uint32_t crc32_calcular(const uint8_t *dados, size_t n);

/* Versao incremental: comece com crc = 0 e encadeie os blocos.
 * crc32_atualizar(crc32_atualizar(0, a, na), b, nb) == crc32 de a||b. */
uint32_t crc32_atualizar(uint32_t crc, const uint8_t *dados, size_t n);

#endif
