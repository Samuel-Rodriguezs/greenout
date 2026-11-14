#include "base_binaria.h"

int decimal_para_binario(unsigned long n, char *saida, size_t cap) {
    char tmp[sizeof n * 8 + 1];
    size_t len = 0;

    do {
        tmp[len++] = (char)('0' + (n & 1UL));
        n >>= 1;
    } while (n != 0);

    if (cap < len + 1) {
        return -1;
    }
    for (size_t i = 0; i < len; i++) {
        saida[i] = tmp[len - 1 - i];
    }
    saida[len] = '\0';
    return 0;
}
