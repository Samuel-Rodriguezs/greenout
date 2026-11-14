#include "shell_parser.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void msg(char *erro, size_t cap, const char *texto) {
    if (erro && cap) snprintf(erro, cap, "%s", texto);
}

/* ---------- buffer de palavra ---------- */

typedef struct {
    char *s;
    size_t n, cap;
} Buf;

static int buf_push(Buf *b, char c) {
    if (b->n + 1 >= b->cap) {
        size_t nc = b->cap ? b->cap * 2 : 16;
        char *ns = realloc(b->s, nc);
        if (!ns) return -1;
        b->s = ns;
        b->cap = nc;
    }
    b->s[b->n++] = c;
    b->s[b->n] = '\0';
    return 0;
}

/* ---------- tokenizador ---------- */

static int tok_push(Token **v, size_t *n, size_t *cap, TokTipo t, char *texto) {
    if (*n == *cap) {
        size_t nc = *cap ? *cap * 2 : 8;
        Token *nv = realloc(*v, nc * sizeof **v);
        if (!nv) return -1;
        *v = nv;
        *cap = nc;
    }
    (*v)[(*n)++] = (Token){t, texto};
    return 0;
}

void sh_liberar_tokens(Token *toks, size_t n) {
    for (size_t i = 0; i < n; i++) free(toks[i].texto);
    free(toks);
}

int sh_tokenizar(const char *linha, Token **toks, size_t *n, char *erro, size_t cap_erro) {
    Token *v = NULL;
    size_t nv = 0, cap = 0;
    const char *p = linha;
    const char *falha = NULL;

    while (!falha) {
        while (isspace((unsigned char)*p)) p++;
        if (!*p) break;
        if (*p == '|' || *p == '<' || *p == '>') {
            TokTipo t = *p == '|' ? TOK_PIPE : *p == '<' ? TOK_ENTRADA : TOK_SAIDA;
            if (*p == '>' && p[1] == '>') {
                t = TOK_ANEXA;
                p++;
            }
            p++;
            if (tok_push(&v, &nv, &cap, t, NULL) < 0) falha = "memoria insuficiente";
            continue;
        }
        /* palavra: concatena trechos sem aspas e entre aspas */
        Buf b = {0};
        if (buf_push(&b, 'x') < 0) { /* garante buffer alocado (palavra "" valida) */
            falha = "memoria insuficiente";
            break;
        }
        b.n = 0;
        b.s[0] = '\0';
        while (*p && !isspace((unsigned char)*p) && *p != '|' && *p != '<' && *p != '>' && !falha) {
            if (*p == '\'') {
                p++;
                while (*p && *p != '\'') {
                    if (buf_push(&b, *p++) < 0) falha = "memoria insuficiente";
                }
                if (!*p) falha = falha ? falha : "aspas simples nao fechadas";
                else p++;
            } else if (*p == '"') {
                p++;
                while (*p && *p != '"') {
                    char c = *p++;
                    if (c == '\\' && (*p == '"' || *p == '\\')) c = *p++;
                    if (buf_push(&b, c) < 0) falha = "memoria insuficiente";
                }
                if (!*p) falha = falha ? falha : "aspas duplas nao fechadas";
                else p++;
            } else if (*p == '\\') {
                p++;
                if (!*p) falha = "barra invertida no fim da linha";
                else if (buf_push(&b, *p++) < 0) falha = "memoria insuficiente";
            } else if (buf_push(&b, *p++) < 0) {
                falha = "memoria insuficiente";
            }
        }
        if (falha || tok_push(&v, &nv, &cap, TOK_PALAVRA, b.s) < 0) {
            free(b.s);
            falha = falha ? falha : "memoria insuficiente";
        }
    }
    if (falha) {
        sh_liberar_tokens(v, nv);
        msg(erro, cap_erro, falha);
        *toks = NULL;
        *n = 0;
        return -1;
    }
    *toks = v;
    *n = nv;
    return 0;
}

/* ---------- parser de pipeline ---------- */

static void comando_liberar(Comando *c) {
    for (int i = 0; i < c->argc; i++) free(c->argv[i]);
    free(c->argv);
    free(c->entrada);
    free(c->saida);
    *c = (Comando){0};
}

void sh_liberar(Pipeline *p) {
    for (int i = 0; i < p->n; i++) comando_liberar(&p->cmds[i]);
    free(p->cmds);
    *p = (Pipeline){0};
}

/* Move a palavra (posse) para o argv do comando */
static int argv_push(Comando *c, char *palavra) {
    char **nv = realloc(c->argv, (size_t)(c->argc + 2) * sizeof *nv);
    if (!nv) return -1;
    c->argv = nv;
    nv[c->argc++] = palavra;
    nv[c->argc] = NULL;
    return 0;
}

int sh_parse(const char *linha, Pipeline *p, char *erro, size_t cap_erro) {
    *p = (Pipeline){0};
    Token *toks;
    size_t nt;
    if (sh_tokenizar(linha, &toks, &nt, erro, cap_erro) < 0) return -1;
    if (nt == 0) {
        sh_liberar_tokens(toks, nt);
        return 0;
    }

    const char *falha = NULL;
    Comando atual = {0};
    for (size_t i = 0; i < nt && !falha; i++) {
        Token *t = &toks[i];
        if (t->tipo == TOK_PALAVRA) {
            if (argv_push(&atual, t->texto) < 0) falha = "memoria insuficiente";
            else t->texto = NULL; /* posse transferida */
        } else if (t->tipo == TOK_PIPE) {
            if (atual.argc == 0) {
                falha = "comando vazio antes de '|'";
                break;
            }
            Comando *nc = realloc(p->cmds, (size_t)(p->n + 1) * sizeof *nc);
            if (!nc) {
                falha = "memoria insuficiente";
                break;
            }
            p->cmds = nc;
            p->cmds[p->n++] = atual;
            atual = (Comando){0};
        } else { /* <, >, >> exigem um arquivo logo depois */
            if (i + 1 >= nt || toks[i + 1].tipo != TOK_PALAVRA) {
                falha = "redirecionamento sem arquivo";
                break;
            }
            char **destino = t->tipo == TOK_ENTRADA ? &atual.entrada : &atual.saida;
            free(*destino); /* o ultimo redirecionamento vence */
            *destino = toks[++i].texto;
            toks[i].texto = NULL;
            if (t->tipo != TOK_ENTRADA) atual.anexar = t->tipo == TOK_ANEXA;
        }
    }
    if (!falha && atual.argc == 0)
        falha = p->n > 0 ? "comando vazio depois de '|'" : "redirecionamento sem comando";
    if (!falha) {
        Comando *nc = realloc(p->cmds, (size_t)(p->n + 1) * sizeof *nc);
        if (!nc) falha = "memoria insuficiente";
        else {
            p->cmds = nc;
            p->cmds[p->n++] = atual;
            atual = (Comando){0};
        }
    }
    sh_liberar_tokens(toks, nt); /* libera o que nao foi transferido */
    if (falha) {
        comando_liberar(&atual);
        sh_liberar(p);
        msg(erro, cap_erro, falha);
        return -1;
    }
    return 0;
}
