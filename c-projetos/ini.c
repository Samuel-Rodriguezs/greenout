#include "ini.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

static char *copia(const char *s, size_t n) {
    char *r = malloc(n + 1);
    if (!r) return NULL;
    memcpy(r, s, n);
    r[n] = 0;
    return r;
}

/* Ajusta [*ini, *ini+*n) para ignorar espacos nas pontas. */
static void aparar(const char **ini, size_t *n) {
    while (*n && isspace((unsigned char)**ini)) { (*ini)++; (*n)--; }
    while (*n && isspace((unsigned char)(*ini)[*n - 1])) (*n)--;
}

void ini_free(Ini *ini) {
    if (!ini) return;
    for (size_t i = 0; i < ini->n; i++) {
        free(ini->e[i].secao);
        free(ini->e[i].chave);
        free(ini->e[i].valor);
    }
    free(ini->e);
    free(ini);
}

const char *ini_get(const Ini *ini, const char *secao, const char *chave) {
    const char *r = NULL;
    for (size_t i = 0; i < ini->n; i++) /* a ultima definicao vence */
        if (!strcmp(ini->e[i].secao, secao) && !strcmp(ini->e[i].chave, chave))
            r = ini->e[i].valor;
    return r;
}

static int add(Ini *ini, const char *sec, const char *k, size_t nk,
               const char *v, size_t nv) {
    IniEntrada *ne = realloc(ini->e, (ini->n + 1) * sizeof *ne);
    if (!ne) return -1;
    ini->e = ne;
    IniEntrada *x = &ne[ini->n];
    x->secao = copia(sec, strlen(sec));
    x->chave = copia(k, nk);
    x->valor = copia(v, nv);
    if (!x->secao || !x->chave || !x->valor) {
        free(x->secao); free(x->chave); free(x->valor);
        return -1;
    }
    ini->n++;
    return 0;
}

Ini *ini_parse(const char *texto, int *linha_erro) {
    Ini *ini = calloc(1, sizeof *ini);
    char *secao = copia("", 0);
    int num = 0;
    if (!ini || !secao) goto erro_mem;
    while (*texto) {
        const char *fim = strchr(texto, '\n');
        size_t n = fim ? (size_t)(fim - texto) : strlen(texto);
        const char *lin = texto;
        texto += n + (fim != NULL);
        num++;
        aparar(&lin, &n);
        if (n == 0 || lin[0] == ';' || lin[0] == '#') continue;
        if (lin[0] == '[') {
            if (lin[n - 1] != ']') goto erro_sintaxe;
            const char *nome = lin + 1;
            size_t nn = n - 2;
            aparar(&nome, &nn);
            char *nova = copia(nome, nn);
            if (!nova) goto erro_mem;
            free(secao);
            secao = nova;
            continue;
        }
        const char *eq = memchr(lin, '=', n);
        if (!eq) goto erro_sintaxe;
        const char *k = lin, *v = eq + 1;
        size_t nk = (size_t)(eq - lin), nv = n - nk - 1;
        aparar(&k, &nk);
        aparar(&v, &nv);
        if (nk == 0) goto erro_sintaxe;
        if (add(ini, secao, k, nk, v, nv)) goto erro_mem;
    }
    free(secao);
    return ini;
erro_sintaxe:
    if (linha_erro) *linha_erro = num;
    free(secao);
    ini_free(ini);
    return NULL;
erro_mem:
    if (linha_erro) *linha_erro = 0;
    free(secao);
    ini_free(ini);
    return NULL;
}
