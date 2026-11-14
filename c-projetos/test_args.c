#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "args.h"

int main(void) {
    char *argv[] = {"prog", "-ab", "-o", "saida.txt", "-nvalor", "-x", "--",
                    "arq1", "-z"};
    int argc = 9;
    Args a;
    args_init(&a, argc, argv, "abo:n:");
    assert(args_proximo(&a) == 'a');
    assert(args_proximo(&a) == 'b');
    assert(args_proximo(&a) == 'o' && strcmp(a.optarg, "saida.txt") == 0);
    assert(args_proximo(&a) == 'n' && strcmp(a.optarg, "valor") == 0);
    assert(args_proximo(&a) == '?' && a.optopt == 'x');
    assert(args_proximo(&a) == -1);
    assert(a.indice == 7 && strcmp(argv[a.indice], "arq1") == 0);

    /* Argumento obrigatorio faltando. */
    char *argv2[] = {"prog", "-o"};
    args_init(&a, 2, argv2, "o:");
    assert(args_proximo(&a) == '?' && a.optopt == 'o');
    assert(args_proximo(&a) == -1);

    /* Para na primeira nao-opcao. */
    char *argv3[] = {"prog", "-a", "arq", "-b"};
    args_init(&a, 4, argv3, "ab");
    assert(args_proximo(&a) == 'a');
    assert(args_proximo(&a) == -1 && a.indice == 2);
    puts("args ok");
    return 0;
}
