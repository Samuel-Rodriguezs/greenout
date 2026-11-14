#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "base64.h"

static void codifica(const char *entrada, const char *esperado) {
    char *e = base64_codificar((const uint8_t *)entrada, strlen(entrada));
    assert(e && strcmp(e, esperado) == 0);
    free(e);
    size_t n;
    uint8_t *d = base64_decodificar(esperado, &n);
    assert(d && n == strlen(entrada) && memcmp(d, entrada, n) == 0);
    free(d);
}

int main(void) {
    /* vetores do RFC 4648 */
    codifica("", "");
    codifica("f", "Zg==");
    codifica("fo", "Zm8=");
    codifica("foo", "Zm9v");
    codifica("foob", "Zm9vYg==");
    codifica("fooba", "Zm9vYmE=");
    codifica("foobar", "Zm9vYmFy");
    codifica("Man", "TWFu");

    /* todos os 256 valores de byte */
    uint8_t todos[256];
    for (int i = 0; i < 256; i++) todos[i] = (uint8_t)i;
    char *e = base64_codificar(todos, 256);
    assert(e && strlen(e) == 344);
    size_t n;
    uint8_t *d = base64_decodificar(e, &n);
    assert(d && n == 256 && memcmp(d, todos, 256) == 0);
    free(e);
    free(d);
    /* bytes que usam '+' e '/' */
    uint8_t esp[] = {0xFB, 0xFF, 0xBF};
    e = base64_codificar(esp, 3);
    assert(e && strcmp(e, "+/+/") == 0);
    free(e);

    /* entradas invalidas */
    assert(base64_decodificar("Zg=", &n) == NULL);       /* tamanho nao multiplo de 4 */
    assert(base64_decodificar("Zg==Zg==", &n) == NULL);  /* padding no meio */
    assert(base64_decodificar("Z===", &n) == NULL);      /* padding demais */
    assert(base64_decodificar("Zm9*", &n) == NULL);      /* caractere invalido */
    assert(base64_decodificar("Zm 9", &n) == NULL);      /* espaco */
    assert(base64_decodificar("=Zg=", &n) == NULL);      /* '=' no inicio */
    assert(base64_decodificar("Zg=A", &n) == NULL);      /* dado depois de '=' */
    d = base64_decodificar("", &n);
    assert(d && n == 0);
    free(d);
    puts("base64 ok");
    return 0;
}
