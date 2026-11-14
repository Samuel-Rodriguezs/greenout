#include <assert.h>

#include "bubble_sort.h"

static void confere(int *v, const int *esperado, size_t n) {
    for (size_t i = 0; i < n; i++) {
        assert(v[i] == esperado[i]);
    }
}

int main(void) {
    int a[] = {5, 2, 9, 1, 5, 6};
    const int ea[] = {1, 2, 5, 5, 6, 9};
    bubble_sort(a, 6);
    confere(a, ea, 6);

    int b[] = {1, 2, 3, 4};
    const int eb[] = {1, 2, 3, 4};
    bubble_sort(b, 4);
    confere(b, eb, 4);

    int c[] = {4, 3, 2, 1, 0, -1};
    const int ec[] = {-1, 0, 1, 2, 3, 4};
    bubble_sort(c, 6);
    confere(c, ec, 6);

    int d[] = {42};
    bubble_sort(d, 1);
    assert(d[0] == 42);

    bubble_sort(d, 0); /* nao deve tocar em nada */
    assert(d[0] == 42);
    return 0;
}
