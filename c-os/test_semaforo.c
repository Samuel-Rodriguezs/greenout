#include <assert.h>
#include <stdio.h>

#include "semaforo.h"

int main(void) {
    assert(sem_criar(-1, 2, 0) == NULL);
    assert(sem_criar(3, 2, 2) == NULL); /* valor acima do maximo */

    /* semaforo contador com 2 recursos */
    Semaforo *s = sem_criar(2, 4, 0);
    int p = -1;
    assert(s && sem_valor(s) == 2);
    assert(sem_wait(s, 1) == SEM_ADQUIRIU && sem_wait(s, 2) == SEM_ADQUIRIU);
    assert(sem_valor(s) == 0 && !sem_trywait(s));

    /* terceiro e quarto bloqueiam, em ordem FIFO */
    assert(sem_wait(s, 3) == SEM_BLOQUEOU && sem_wait(s, 4) == SEM_BLOQUEOU);
    assert(sem_esperando(s) == 2);
    assert(sem_wait(s, 3) == SEM_ERRO); /* ja esta na fila */

    /* signal entrega direto ao primeiro da fila; valor segue 0 */
    assert(sem_signal(s, &p) == 1 && p == 3 && sem_valor(s) == 0);
    assert(sem_signal(s, &p) == 1 && p == 4 && sem_esperando(s) == 0);

    /* sem esperando, signal incrementa */
    assert(sem_signal(s, &p) == 0 && sem_valor(s) == 1);
    assert(sem_trywait(s) == 1 && sem_valor(s) == 0);
    assert(sem_signal(s, NULL) == 0 && sem_signal(s, NULL) == 0 && sem_valor(s) == 2);

    /* fila cheia */
    sem_trywait(s);
    sem_trywait(s);
    for (int i = 10; i < 14; i++) assert(sem_wait(s, i) == SEM_BLOQUEOU);
    assert(sem_wait(s, 99) == SEM_ERRO);
    sem_destruir(s);

    /* mutex (binario): signal acima do maximo e erro */
    Semaforo *m = sem_criar(1, 2, 1);
    assert(sem_wait(m, 1) == SEM_ADQUIRIU);
    assert(sem_wait(m, 2) == SEM_BLOQUEOU);
    assert(sem_signal(m, &p) == 1 && p == 2); /* passa a posse para 2 */
    assert(sem_signal(m, &p) == 0 && sem_valor(m) == 1);
    assert(sem_signal(m, &p) == SEM_ERRO && sem_valor(m) == 1);
    sem_destruir(m);

    /* produtor/consumidor: vagas=3, itens=0; 3 producoes, 3 consumos */
    Semaforo *vagas = sem_criar(3, 2, 3), *itens = sem_criar(0, 2, 3);
    for (int i = 0; i < 3; i++) {
        assert(sem_wait(vagas, 1) == SEM_ADQUIRIU);
        assert(sem_signal(itens, NULL) == 0);
    }
    assert(sem_wait(vagas, 1) == SEM_BLOQUEOU); /* buffer cheio: produtor dorme */
    assert(sem_valor(itens) == 3);
    assert(sem_wait(itens, 2) == SEM_ADQUIRIU); /* consumidor retira */
    assert(sem_signal(vagas, &p) == 1 && p == 1); /* acorda o produtor */
    sem_destruir(vagas);
    sem_destruir(itens);

    /* sem fila de espera (cap 0): nunca bloqueia, so erro */
    Semaforo *z = sem_criar(0, 0, 0);
    assert(sem_wait(z, 1) == SEM_ERRO);
    sem_destruir(z);
    sem_destruir(NULL);

    puts("test_semaforo ok");
    return 0;
}
