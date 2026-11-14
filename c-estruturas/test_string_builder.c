#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "string_builder.h"

int main(void) {
    StringBuilder *sb = sb_novo();
    assert(sb_tam(sb) == 0 && strcmp(sb_str(sb), "") == 0);
    assert(sb_anexar(sb, "") && sb_tam(sb) == 0);
    assert(sb_anexar(sb, "ola") && sb_anexar_char(sb, ',') && sb_anexar_char(sb, ' '));
    assert(sb_anexar(sb, "mundo"));
    assert(strcmp(sb_str(sb), "ola, mundo") == 0 && sb_tam(sb) == 10);
    assert(sb_anexar_n(sb, "!!!ignorado", 3));
    assert(strcmp(sb_str(sb), "ola, mundo!!!") == 0);
    assert(sb_anexar_fmt(sb, " %d-%s-%05.1f", 42, "x", 3.14159));
    assert(strcmp(sb_str(sb), "ola, mundo!!! 42-x-003.1") == 0);
    assert(sb_anexar_fmt(sb, "%s", ""));            /* formato que gera vazio */
    assert(strlen(sb_str(sb)) == sb_tam(sb));

    /* crescimento: muitos anexos e uma string longa de uma vez */
    sb_limpar(sb);
    assert(sb_tam(sb) == 0 && sb_str(sb)[0] == '\0');
    for (int i = 0; i < 5000; i++) assert(sb_anexar_char(sb, (char)('a' + i % 26)));
    assert(sb_tam(sb) == 5000 && strlen(sb_str(sb)) == 5000);
    assert(sb_str(sb)[4999] == (char)('a' + 4999 % 26));
    char longa[3001];
    memset(longa, 'z', 3000);
    longa[3000] = '\0';
    assert(sb_anexar_fmt(sb, "%s", longa) && sb_tam(sb) == 8000);

    char *s = sb_destacar(sb);
    assert(s && strlen(s) == 8000);
    free(s);
    assert(sb_tam(sb) == 0 && sb_anexar(sb, "de novo"));
    assert(strcmp(sb_str(sb), "de novo") == 0);
    sb_liberar(sb);
    sb_liberar(NULL);
    puts("string_builder ok");
    return 0;
}
