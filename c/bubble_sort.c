#include "bubble_sort.h"

#include <stdbool.h>

void bubble_sort(int *v, size_t n) {
    for (size_t fim = n; fim > 1; fim--) {
        bool trocou = false;
        for (size_t i = 0; i + 1 < fim; i++) {
            if (v[i] > v[i + 1]) {
                int tmp = v[i];
                v[i] = v[i + 1];
                v[i + 1] = tmp;
                trocou = true;
            }
        }
        if (!trocou) {
            break;
        }
    }
}
