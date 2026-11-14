#include "json.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

static JNo *valor(const char **p);

static void ws(const char **p) {
    while (isspace((unsigned char)**p)) (*p)++;
}

static JNo *novo(JTipo t) {
    JNo *n = calloc(1, sizeof *n);
    if (n) n->tipo = t;
    return n;
}

/* Le string entre aspas (escapes basicos) e devolve copia alocada. */
static char *le_string(const char **p) {
    if (**p != '"') return NULL;
    (*p)++;
    size_t cap = 16, n = 0;
    char *s = malloc(cap);
    if (!s) return NULL;
    while (**p && **p != '"') {
        char c = *(*p)++;
        if (c == '\\') {
            c = *(*p)++;
            switch (c) {
            case 'n': c = '\n'; break;
            case 't': c = '\t'; break;
            case '"': case '\\': case '/': break;
            default: free(s); return NULL;
            }
        }
        if (n + 1 >= cap) {
            cap *= 2;
            char *t = realloc(s, cap);
            if (!t) { free(s); return NULL; }
            s = t;
        }
        s[n++] = c;
    }
    if (**p != '"') { free(s); return NULL; }
    (*p)++;
    s[n] = 0;
    return s;
}

void json_free(JNo *no) {
    if (!no) return;
    for (size_t i = 0; i < no->n; i++) {
        json_free(no->itens[i]);
        if (no->chaves) free(no->chaves[i]);
    }
    free(no->itens);
    free(no->chaves);
    free(no->str);
    free(no);
}

/* Acrescenta filho (e chave, se objeto) ao no. Retorna 0 em sucesso. */
static int adiciona(JNo *pai, JNo *filho, char *chave) {
    JNo **it = realloc(pai->itens, (pai->n + 1) * sizeof *it);
    if (!it) return -1;
    pai->itens = it;
    if (pai->tipo == J_OBJ) {
        char **ch = realloc(pai->chaves, (pai->n + 1) * sizeof *ch);
        if (!ch) return -1;
        pai->chaves = ch;
        ch[pai->n] = chave;
    }
    it[pai->n++] = filho;
    return 0;
}

static JNo *colecao(const char **p, JTipo t, char fim) {
    JNo *no = novo(t);
    if (!no) return NULL;
    (*p)++;
    ws(p);
    if (**p == fim) { (*p)++; return no; }
    for (;;) {
        char *chave = NULL;
        ws(p);
        if (t == J_OBJ) {
            chave = le_string(p);
            ws(p);
            if (!chave || *(*p)++ != ':') { free(chave); json_free(no); return NULL; }
        }
        JNo *f = valor(p);
        if (!f || adiciona(no, f, chave)) {
            free(chave); json_free(f); json_free(no); return NULL;
        }
        ws(p);
        if (**p == ',') { (*p)++; continue; }
        if (**p == fim) { (*p)++; return no; }
        json_free(no);
        return NULL;
    }
}

static JNo *valor(const char **p) {
    ws(p);
    JNo *n;
    if (**p == '{') return colecao(p, J_OBJ, '}');
    if (**p == '[') return colecao(p, J_ARR, ']');
    if (**p == '"') {
        char *s = le_string(p);
        if (!s) return NULL;
        if (!(n = novo(J_STR))) { free(s); return NULL; }
        n->str = s;
        return n;
    }
    if (!strncmp(*p, "true", 4)) { *p += 4; n = novo(J_BOOL); if (n) n->b = 1; return n; }
    if (!strncmp(*p, "false", 5)) { *p += 5; return novo(J_BOOL); }
    if (!strncmp(*p, "null", 4)) { *p += 4; return novo(J_NULL); }
    if (**p == '-' || isdigit((unsigned char)**p)) {
        char *fim;
        double d = strtod(*p, &fim);
        if (fim == *p) return NULL;
        *p = fim;
        if ((n = novo(J_NUM))) n->num = d;
        return n;
    }
    return NULL;
}

JNo *json_parse(const char *texto) {
    const char *p = texto;
    JNo *r = valor(&p);
    if (!r) return NULL;
    ws(&p);
    if (*p) { json_free(r); return NULL; }
    return r;
}

JNo *json_obter(const JNo *obj, const char *chave) {
    if (!obj || obj->tipo != J_OBJ) return NULL;
    for (size_t i = 0; i < obj->n; i++)
        if (!strcmp(obj->chaves[i], chave)) return obj->itens[i];
    return NULL;
}
