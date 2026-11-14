#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "shell_parser.h"

static void esperar_erro(const char *linha, const char *trecho) {
    Pipeline p;
    char erro[100] = "";
    assert(sh_parse(linha, &p, erro, sizeof erro) == -1);
    assert(p.n == 0 && p.cmds == NULL);
    assert(strstr(erro, trecho) != NULL);
}

int main(void) {
    Token *t;
    size_t n;
    char erro[100];

    /* tokenizacao simples */
    assert(sh_tokenizar("  ls   -l  /tmp ", &t, &n, erro, sizeof erro) == 0);
    assert(n == 3 && t[0].tipo == TOK_PALAVRA && strcmp(t[0].texto, "ls") == 0);
    assert(strcmp(t[1].texto, "-l") == 0 && strcmp(t[2].texto, "/tmp") == 0);
    sh_liberar_tokens(t, n);

    /* operadores colados nas palavras */
    assert(sh_tokenizar("a|b>c>>d<e", &t, &n, erro, sizeof erro) == 0);
    assert(n == 9);
    assert(t[1].tipo == TOK_PIPE && t[3].tipo == TOK_SAIDA);
    assert(t[5].tipo == TOK_ANEXA && t[7].tipo == TOK_ENTRADA);
    assert(t[1].texto == NULL && strcmp(t[8].texto, "e") == 0);
    sh_liberar_tokens(t, n);

    /* aspas, escapes e concatenacao */
    assert(sh_tokenizar("echo \"a b\" 'c|d' e\\ f x\"y z\"w \"q\\\"r\\\\\" ''", &t, &n, erro, sizeof erro) == 0);
    assert(n == 7);
    assert(strcmp(t[1].texto, "a b") == 0);
    assert(strcmp(t[2].texto, "c|d") == 0);
    assert(strcmp(t[3].texto, "e f") == 0);
    assert(strcmp(t[4].texto, "xy zw") == 0);
    assert(strcmp(t[5].texto, "q\"r\\") == 0);
    assert(t[6].tipo == TOK_PALAVRA && t[6].texto[0] == '\0'); /* palavra vazia */
    sh_liberar_tokens(t, n);

    /* operador entre aspas e so texto; dentro de aspas simples \ e literal */
    assert(sh_tokenizar("echo '>' \">>\" 'a\\b' \\|", &t, &n, erro, sizeof erro) == 0);
    assert(n == 5 && t[1].tipo == TOK_PALAVRA && strcmp(t[1].texto, ">") == 0);
    assert(strcmp(t[2].texto, ">>") == 0 && strcmp(t[3].texto, "a\\b") == 0);
    assert(t[4].tipo == TOK_PALAVRA && strcmp(t[4].texto, "|") == 0);
    sh_liberar_tokens(t, n);

    /* erros de tokenizacao */
    assert(sh_tokenizar("echo 'abc", &t, &n, erro, sizeof erro) == -1);
    assert(t == NULL && n == 0 && strstr(erro, "simples"));
    assert(sh_tokenizar("echo \"abc", &t, &n, erro, sizeof erro) == -1 && strstr(erro, "duplas"));
    assert(sh_tokenizar("echo abc\\", &t, &n, erro, sizeof erro) == -1 && strstr(erro, "barra"));
    assert(sh_tokenizar("echo 'a", &t, &n, NULL, 0) == -1); /* sem buffer de erro */

    /* pipeline simples */
    Pipeline p;
    assert(sh_parse("ls -l", &p, erro, sizeof erro) == 0);
    assert(p.n == 1 && p.cmds[0].argc == 2 && strcmp(p.cmds[0].argv[0], "ls") == 0);
    assert(p.cmds[0].argv[2] == NULL && !p.cmds[0].entrada && !p.cmds[0].saida);
    sh_liberar(&p);

    /* pipeline com 3 estagios e redirecionamentos */
    assert(sh_parse("cat < in.txt | grep \"foo bar\" | sort -r > out.txt", &p, erro, sizeof erro) == 0);
    assert(p.n == 3);
    assert(strcmp(p.cmds[0].argv[0], "cat") == 0 && strcmp(p.cmds[0].entrada, "in.txt") == 0);
    assert(p.cmds[1].argc == 2 && strcmp(p.cmds[1].argv[1], "foo bar") == 0);
    assert(p.cmds[1].entrada == NULL && p.cmds[1].saida == NULL);
    assert(p.cmds[2].argc == 2 && strcmp(p.cmds[2].saida, "out.txt") == 0 && !p.cmds[2].anexar);
    sh_liberar(&p);

    /* append, redirecionamento antes do comando e o ultimo vence */
    assert(sh_parse(">> log.txt echo oi > a > b", &p, erro, sizeof erro) == 0);
    assert(p.n == 1 && p.cmds[0].argc == 2 && strcmp(p.cmds[0].argv[0], "echo") == 0);
    assert(strcmp(p.cmds[0].saida, "b") == 0 && p.cmds[0].anexar == 0);
    sh_liberar(&p);
    assert(sh_parse("echo oi>>f", &p, erro, sizeof erro) == 0);
    assert(strcmp(p.cmds[0].saida, "f") == 0 && p.cmds[0].anexar == 1);
    sh_liberar(&p);

    /* linha vazia ou so espacos */
    assert(sh_parse("", &p, erro, sizeof erro) == 0 && p.n == 0);
    sh_liberar(&p);
    assert(sh_parse("   \t ", &p, erro, sizeof erro) == 0 && p.n == 0);
    sh_liberar(&p);

    /* erros sintaticos: nada vaza (ASan) e p fica vazio */
    esperar_erro("| ls", "antes");
    esperar_erro("ls |", "depois");
    esperar_erro("ls | | wc", "antes");
    esperar_erro("ls >", "sem arquivo");
    esperar_erro("ls > | wc", "sem arquivo");
    esperar_erro("ls <", "sem arquivo");
    esperar_erro("> arq", "sem comando");
    esperar_erro("echo 'x", "simples");
    esperar_erro("a b c | d > e | | f", "antes");

    puts("test_shell_parser ok");
    return 0;
}
