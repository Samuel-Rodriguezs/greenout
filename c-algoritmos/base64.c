#include "base64.h"
#include <stdlib.h>
#include <string.h>

static const char ALFABETO[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char *base64_codificar(const uint8_t *d, size_t n) {
    size_t saida = 4 * ((n + 2) / 3);
    char *out = malloc(saida + 1);
    if (!out) return NULL;
    size_t k = 0;
    for (size_t i = 0; i < n; i += 3) {
        uint32_t v = (uint32_t)d[i] << 16;
        if (i + 1 < n) v |= (uint32_t)d[i + 1] << 8;
        if (i + 2 < n) v |= d[i + 2];
        out[k++] = ALFABETO[(v >> 18) & 63];
        out[k++] = ALFABETO[(v >> 12) & 63];
        out[k++] = (i + 1 < n) ? ALFABETO[(v >> 6) & 63] : '=';
        out[k++] = (i + 2 < n) ? ALFABETO[v & 63] : '=';
    }
    out[k] = '\0';
    return out;
}

static int valor(char c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

uint8_t *base64_decodificar(const char *t, size_t *saida_n) {
    size_t n = strlen(t);
    if (n % 4 != 0) return NULL;
    size_t pad = 0;
    if (n > 0 && t[n - 1] == '=') pad++;
    if (n > 1 && t[n - 2] == '=') pad++;
    size_t total = n / 4 * 3 - pad;
    uint8_t *out = malloc(total + 1);
    if (!out) return NULL;
    size_t k = 0;
    for (size_t i = 0; i < n; i += 4) {
        int ultimo = (i + 4 == n);
        int v[4];
        for (int j = 0; j < 4; j++) {
            char c = t[i + j];
            if (c == '=') {
                /* '=' so vale nas ultimas 'pad' posicoes do ultimo bloco */
                if (!ultimo || (size_t)(4 - j) > pad) { free(out); return NULL; }
                v[j] = 0;
            } else {
                v[j] = valor(c);
                if (v[j] < 0 || (ultimo && (size_t)(4 - j) <= pad)) { free(out); return NULL; }
            }
        }
        uint32_t w = ((uint32_t)v[0] << 18) | ((uint32_t)v[1] << 12) |
                     ((uint32_t)v[2] << 6) | (uint32_t)v[3];
        out[k++] = (uint8_t)(w >> 16);
        if (!(ultimo && pad == 2)) out[k++] = (uint8_t)(w >> 8);
        if (!(ultimo && pad >= 1)) out[k++] = (uint8_t)w;
    }
    *saida_n = k;
    return out;
}
