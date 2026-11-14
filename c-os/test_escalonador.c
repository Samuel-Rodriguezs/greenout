#include <assert.h>
#include <math.h>
#include <stdio.h>

#include "escalonador.h"

#define IGUAL(a, b) (fabs((a) - (b)) < 1e-9)

int main(void) {
    Resultado r[5];
    Metricas m;

    /* Silberschatz: P1=24, P2=3, P3=3 chegando em 0 */
    Proc a[] = {{1, 0, 24, 0}, {2, 0, 3, 0}, {3, 0, 3, 0}};
    assert(esc_fcfs(a, 3, r, &m) == 0);
    assert(r[0].espera == 0 && r[1].espera == 24 && r[2].espera == 27);
    assert(IGUAL(m.espera_media, 17.0) && m.tempo_total == 30);
    assert(r[2].termino == 30 && r[1].resposta == 24);

    /* SJF: ordem P2, P3, P1 -> esperas 6, 0, 3 */
    assert(esc_sjf(a, 3, r, &m) == 0);
    assert(r[0].espera == 6 && r[1].espera == 0 && r[2].espera == 3);
    assert(IGUAL(m.espera_media, 3.0) && IGUAL(m.retorno_medio, 13.0));

    /* Round Robin q=4: P1 espera 6, P2 4, P3 7 (media 17/3) */
    assert(esc_rr(a, 3, 4, r, &m) == 0);
    assert(r[0].termino == 30 && r[1].termino == 7 && r[2].termino == 10);
    assert(r[0].espera == 6 && r[1].espera == 4 && r[2].espera == 7);
    assert(r[0].resposta == 0 && r[1].resposta == 4 && r[2].resposta == 7);
    assert(IGUAL(m.espera_media, 17.0 / 3.0));

    /* SJF nao-preemptivo com chegadas: P1(0,7) P2(2,4) P3(4,1) P4(5,4) */
    Proc b[] = {{1, 0, 7, 0}, {2, 2, 4, 0}, {3, 4, 1, 0}, {4, 5, 4, 0}};
    assert(esc_sjf(b, 4, r, &m) == 0);
    assert(r[0].termino == 7 && r[2].termino == 8 && r[1].termino == 12 && r[3].termino == 16);
    assert(r[0].espera == 0 && r[1].espera == 6 && r[2].espera == 3 && r[3].espera == 7);
    assert(IGUAL(m.espera_media, 4.0));

    /* Prioridade (menor = mais urgente), todos em t=0:
     * ordem P2, P5, P1, P3, P4 -> espera media 8.2, retorno medio 12 */
    Proc c[] = {{1, 0, 10, 3}, {2, 0, 1, 1}, {3, 0, 2, 4}, {4, 0, 1, 5}, {5, 0, 5, 2}};
    assert(esc_prioridade(c, 5, r, &m) == 0);
    assert(r[1].espera == 0 && r[4].espera == 1 && r[0].espera == 6);
    assert(r[2].espera == 16 && r[3].espera == 18);
    assert(IGUAL(m.espera_media, 8.2) && IGUAL(m.retorno_medio, 12.0));

    /* RR com chegadas: P1(0,5) P2(1,3) P3(2,1), q=2 -> termina em 9, 8, 5 */
    Proc d[] = {{1, 0, 5, 0}, {2, 1, 3, 0}, {3, 2, 1, 0}};
    assert(esc_rr(d, 3, 2, r, &m) == 0);
    assert(r[0].termino == 9 && r[1].termino == 8 && r[2].termino == 5);
    assert(r[0].espera == 4 && r[1].espera == 4 && r[2].espera == 2);
    assert(r[0].resposta == 0 && r[1].resposta == 1 && r[2].resposta == 2);

    /* CPU ociosa antes da primeira chegada (todos os algoritmos) */
    Proc e[] = {{1, 5, 2, 0}};
    assert(esc_fcfs(e, 1, r, &m) == 0 && r[0].termino == 7 && r[0].espera == 0);
    assert(esc_sjf(e, 1, r, &m) == 0 && r[0].termino == 7);
    assert(esc_prioridade(e, 1, r, &m) == 0 && r[0].termino == 7);
    assert(esc_rr(e, 1, 1, r, &m) == 0 && r[0].termino == 7 && r[0].resposta == 0);

    /* lacuna no meio: P1(0,2), P2(10,1) */
    Proc f[] = {{1, 0, 2, 0}, {2, 10, 1, 0}};
    assert(esc_rr(f, 2, 3, r, &m) == 0 && r[1].termino == 11 && m.tempo_total == 11);
    assert(esc_fcfs(f, 2, r, &m) == 0 && r[1].termino == 11 && r[1].espera == 0);

    /* quantum maior que todos os bursts equivale a FCFS */
    Resultado r2[3];
    assert(esc_rr(a, 3, 100, r, NULL) == 0 && esc_fcfs(a, 3, r2, NULL) == 0);
    for (int i = 0; i < 3; i++) assert(r[i].termino == r2[i].termino);

    /* desempate por ordem do vetor quando tudo empata */
    Proc g[] = {{7, 0, 3, 1}, {8, 0, 3, 1}};
    assert(esc_sjf(g, 2, r, NULL) == 0 && r[0].termino == 3 && r[1].termino == 6);
    assert(esc_prioridade(g, 2, r, NULL) == 0 && r[0].termino == 3);

    /* entradas invalidas e vazia */
    Proc h[] = {{1, 0, 0, 0}};
    assert(esc_fcfs(h, 1, r, &m) == -1 && esc_rr(h, 1, 1, r, &m) == -1);
    assert(esc_rr(a, 3, 0, r, &m) == -1);
    assert(esc_fcfs(a, 0, r, &m) == 0 && m.tempo_total == 0 && IGUAL(m.espera_media, 0.0));
    assert(esc_rr(a, 0, 2, r, &m) == 0 && m.tempo_total == 0);

    puts("test_escalonador ok");
    return 0;
}
