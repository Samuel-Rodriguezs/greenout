#include <assert.h>
#include <stdio.h>
#include "countingsort.h"

int main(void) {
    assert(countingsort(NULL, 0) == 0);
    int um[] = {3}; assert(countingsort(um, 1) == 0 && um[0] == 3);
    int a[] = {5, -3, 0, 5, -3, 100, 2, 2};
    assert(countingsort(a, 8) == 0);
    int esp[] = {-3, -3, 0, 2, 2, 5, 5, 100};
    for (int i = 0; i < 8; i++) assert(a[i] == esp[i]);
    int iguais[] = {7, 7, 7};
    assert(countingsort(iguais, 3) == 0 && iguais[0] == 7 && iguais[2] == 7);
    /* faixa enorme deve ser recusada sem alterar o vetor */
    int grande[] = {-2147483647 - 1, 2147483647, 0};
    assert(countingsort(grande, 3) == -1);
    assert(grande[0] == -2147483647 - 1 && grande[1] == 2147483647 && grande[2] == 0);
    int neg[] = {-1, -2, -3};
    assert(countingsort(neg, 3) == 0 && neg[0] == -3 && neg[2] == -1);
    puts("countingsort ok");
    return 0;
}
