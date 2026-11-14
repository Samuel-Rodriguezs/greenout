#include <assert.h>
#include <string.h>

#include "meu_string.h"

int main(void) {
    assert(meu_strlen("") == 0);
    assert(meu_strlen("a") == 1);
    assert(meu_strlen("laboratorio") == 11);

    char par[] = "abcd";
    assert(strcmp(meu_strrev(par), "dcba") == 0);
    char impar[] = "abcde";
    assert(strcmp(meu_strrev(impar), "edcba") == 0);
    char vazia[] = "";
    assert(strcmp(meu_strrev(vazia), "") == 0);
    char um[] = "x";
    assert(strcmp(meu_strrev(um), "x") == 0);
    return 0;
}
