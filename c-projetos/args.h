#ifndef ARGS_H
#define ARGS_H

/* Parser de argumentos estilo getopt (sem estado global).
 * optstring: letras de opcoes; ':' apos a letra indica argumento obrigatorio.
 * Suporta agrupamento (-abc), argumento colado (-ovalor) ou separado
 * (-o valor) e "--" para encerrar opcoes. */
typedef struct {
    int argc;
    char **argv;
    const char *optstring;
    int indice;   /* proximo argv a processar */
    int pos;      /* posicao dentro de um grupo (-abc) */
    char *optarg; /* argumento da ultima opcao, se houver */
    int optopt;   /* opcao invalida / sem argumento */
} Args;

void args_init(Args *a, int argc, char **argv, const char *optstring);
/* Retorna a letra da opcao, '?' para opcao invalida ou argumento faltando,
 * e -1 ao acabar as opcoes (a->indice aponta para o primeiro nao-opcao). */
int args_proximo(Args *a);

#endif
