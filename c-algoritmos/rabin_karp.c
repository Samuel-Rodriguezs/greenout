#include "rabin_karp.h"
#include <stdint.h>
#include <string.h>

#define BASE 257ULL
#define MOD  1000000007ULL

static long varrer(const char *t, const char *p, int so_primeiro) {
    size_t n = strlen(t), m = strlen(p);
    if (m == 0) return 0;
    if (m > n) return so_primeiro ? -1 : 0;
    /* pot = BASE^(m-1) mod MOD */
    uint64_t pot = 1, hp = 0, ht = 0;
    for (size_t i = 0; i + 1 < m; i++) pot = pot * BASE % MOD;
    for (size_t i = 0; i < m; i++) {
        hp = (hp * BASE + (unsigned char)p[i]) % MOD;
        ht = (ht * BASE + (unsigned char)t[i]) % MOD;
    }
    long achados = 0;
    for (size_t i = 0; ; i++) {
        if (hp == ht && memcmp(t + i, p, m) == 0) {
            if (so_primeiro) return (long)i;
            achados++;
        }
        if (i + m >= n) break;
        /* remove t[i], adiciona t[i+m] */
        ht = (ht + MOD - (unsigned char)t[i] * pot % MOD) % MOD;
        ht = (ht * BASE + (unsigned char)t[i + m]) % MOD;
    }
    return so_primeiro ? -1 : achados;
}

long rabin_karp_buscar(const char *texto, const char *padrao) { return varrer(texto, padrao, 1); }
long rabin_karp_contar(const char *texto, const char *padrao) { return varrer(texto, padrao, 0); }
