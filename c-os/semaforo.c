#include "semaforo.h"

#include <stdlib.h>

struct Semaforo {
    int valor;
    int maximo;
    int *fila;
    size_t cap, ini, n;
};

Semaforo *sem_criar(int valor, size_t cap_fila, int maximo) {
    if (valor < 0 || maximo < 0 || (maximo > 0 && valor > maximo)) return NULL;
    Semaforo *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    s->fila = calloc(cap_fila ? cap_fila : 1, sizeof(int));
    if (!s->fila) {
        free(s);
        return NULL;
    }
    s->valor = valor;
    s->maximo = maximo;
    s->cap = cap_fila;
    return s;
}

void sem_destruir(Semaforo *s) {
    if (!s) return;
    free(s->fila);
    free(s);
}

int sem_wait(Semaforo *s, int pid) {
    if (s->valor > 0) {
        s->valor--;
        return SEM_ADQUIRIU;
    }
    if (s->n == s->cap) return SEM_ERRO;
    for (size_t i = 0; i < s->n; i++)
        if (s->fila[(s->ini + i) % s->cap] == pid) return SEM_ERRO;
    s->fila[(s->ini + s->n++) % s->cap] = pid;
    return SEM_BLOQUEOU;
}

int sem_trywait(Semaforo *s) {
    if (s->valor == 0) return 0;
    s->valor--;
    return 1;
}

int sem_signal(Semaforo *s, int *acordado) {
    if (s->n > 0) { /* entrega direta: o valor continua 0 */
        if (acordado) *acordado = s->fila[s->ini];
        s->ini = (s->ini + 1) % s->cap;
        s->n--;
        return 1;
    }
    if (s->maximo > 0 && s->valor >= s->maximo) return SEM_ERRO;
    s->valor++;
    return 0;
}

int sem_valor(const Semaforo *s) { return s->valor; }
size_t sem_esperando(const Semaforo *s) { return s->n; }
