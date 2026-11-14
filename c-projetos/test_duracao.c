#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "duracao.h"

int main(void) {
    char b[64];
    duracao_formatar(93784, b, sizeof b);
    assert(strcmp(b, "1d 2h 3m 4s") == 0);
    duracao_formatar(3600, b, sizeof b);
    assert(strcmp(b, "1h") == 0);
    duracao_formatar(0, b, sizeof b);
    assert(strcmp(b, "0s") == 0);
    duracao_formatar(61, b, sizeof b);
    assert(strcmp(b, "1m 1s") == 0);
    /* Buffer pequeno: trunca, mas informa o tamanho total. */
    char peq[4];
    assert(duracao_formatar(93784, peq, sizeof peq) == 11);
    assert(strcmp(peq, "1d ") == 0);

    duracao_relogio(3725, b, sizeof b);
    assert(strcmp(b, "01:02:05") == 0);
    duracao_relogio(360000, b, sizeof b);
    assert(strcmp(b, "100:00:00") == 0);

    long long s;
    assert(duracao_parse("1d2h3m4s", &s) == 0 && s == 93784);
    assert(duracao_parse("90m", &s) == 0 && s == 5400);
    assert(duracao_parse("45s30m", &s) == 0 && s == 1845);
    assert(duracao_parse("", &s) == -1);
    assert(duracao_parse("10", &s) == -1);
    assert(duracao_parse("5x", &s) == -1);
    assert(duracao_parse("1h1h", &s) == -1);
    assert(duracao_parse("h", &s) == -1);

    duracao_hora12(15 * 3600 + 5 * 60, b, sizeof b);
    assert(strcmp(b, "03:05 PM") == 0);
    duracao_hora12(0, b, sizeof b);
    assert(strcmp(b, "12:00 AM") == 0);
    duracao_hora12(12 * 3600, b, sizeof b);
    assert(strcmp(b, "12:00 PM") == 0);
    puts("duracao ok");
    return 0;
}
