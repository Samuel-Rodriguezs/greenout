#include <assert.h>
#include <string.h>

#include "base_binaria.h"

int main(void) {
    char buf[16];

    assert(decimal_para_binario(0, buf, sizeof buf) == 0);
    assert(strcmp(buf, "0") == 0);
    assert(decimal_para_binario(1, buf, sizeof buf) == 0);
    assert(strcmp(buf, "1") == 0);
    assert(decimal_para_binario(10, buf, sizeof buf) == 0);
    assert(strcmp(buf, "1010") == 0);
    assert(decimal_para_binario(255, buf, sizeof buf) == 0);
    assert(strcmp(buf, "11111111") == 0);

    /* "1010" precisa de 5 bytes */
    assert(decimal_para_binario(10, buf, 5) == 0);
    assert(decimal_para_binario(10, buf, 4) == -1);
    assert(decimal_para_binario(0, buf, 1) == -1);

    char grande[80];
    assert(decimal_para_binario(1UL << 20, grande, sizeof grande) == 0);
    assert(strlen(grande) == 21 && grande[0] == '1' && grande[20] == '0');
    return 0;
}
