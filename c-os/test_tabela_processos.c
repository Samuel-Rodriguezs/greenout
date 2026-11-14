#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "tabela_processos.h"

int main(void) {
    assert(tp_criar(0) == NULL);
    TabelaProc *t = tp_criar(3);
    assert(t && tp_total(t) == 0 && tp_em_execucao(t) == -1);

    int a = tp_criar_proc(t, 0);
    int b = tp_criar_proc(t, a);
    assert(a == 1 && b == 2 && tp_ppid(t, b) == a);
    assert(tp_estado(t, a) == PROC_NOVO && tp_contar(t, PROC_NOVO) == 2);
    assert(tp_criar_proc(t, 99) == -1); /* pai inexistente */

    /* ciclo de vida completo */
    assert(tp_despachar(t, a) == TP_ERR_TRANSICAO); /* NOVO nao executa */
    assert(tp_admitir(t, a) == TP_OK && tp_admitir(t, b) == TP_OK);
    assert(tp_admitir(t, a) == TP_ERR_TRANSICAO);   /* ja PRONTO */
    assert(tp_despachar(t, a) == TP_OK);
    assert(tp_em_execucao(t) == a);
    assert(tp_despachar(t, b) == TP_ERR_CPU_OCUPADA);

    /* preempcao devolve a fila de prontos; b assume a CPU */
    assert(tp_preemptar(t, a) == TP_OK && tp_estado(t, a) == PROC_PRONTO);
    assert(tp_despachar(t, b) == TP_OK);
    assert(tp_bloquear(t, b) == TP_OK && tp_estado(t, b) == PROC_BLOQUEADO);
    assert(tp_em_execucao(t) == -1);
    assert(tp_bloquear(t, b) == TP_ERR_TRANSICAO);
    assert(tp_despachar(t, b) == TP_ERR_TRANSICAO); /* bloqueado nao executa */
    assert(tp_desbloquear(t, b) == TP_OK && tp_estado(t, b) == PROC_PRONTO);
    assert(tp_desbloquear(t, b) == TP_ERR_TRANSICAO);
    assert(tp_contar(t, PROC_PRONTO) == 2);

    /* terminar so a partir de EXECUTANDO */
    assert(tp_terminar(t, a, 0) == TP_ERR_TRANSICAO);
    assert(tp_despachar(t, a) == TP_OK && tp_terminar(t, a, 42) == TP_OK);
    int cod = 0;
    assert(tp_coletar(t, b, &cod) == TP_ERR_TRANSICAO); /* b nao terminou */
    assert(tp_coletar(t, a, &cod) == TP_OK && cod == 42);
    assert(tp_estado(t, a) == -1 && tp_total(t) == 1);
    assert(tp_coletar(t, a, &cod) == TP_ERR_PID);
    assert(tp_ppid(t, b) == 0); /* b virou orfao */

    /* pid nunca e reutilizado, mas a vaga sim */
    int c = tp_criar_proc(t, 0), d = tp_criar_proc(t, 0);
    assert(c == 3 && d == 4 && tp_total(t) == 3);
    assert(tp_criar_proc(t, 0) == -1); /* tabela cheia */

    /* kill de qualquer estado nao terminado */
    assert(tp_matar(t, c) == TP_OK && tp_estado(t, c) == PROC_TERMINADO);
    assert(tp_matar(t, c) == TP_ERR_TRANSICAO);
    assert(tp_coletar(t, c, &cod) == TP_OK && cod == -9);
    assert(tp_matar(t, 77) == TP_ERR_PID);

    /* pids invalidos */
    assert(tp_admitir(t, 0) == TP_ERR_PID && tp_admitir(t, -3) == TP_ERR_PID);
    assert(tp_estado(t, 0) == -1);
    assert(strcmp(tp_nome_estado(PROC_BLOQUEADO), "bloqueado") == 0);
    assert(strcmp(tp_nome_estado(PROC_NUM_ESTADOS), "?") == 0);
    tp_destruir(t);
    tp_destruir(NULL);

    puts("test_tabela_processos ok");
    return 0;
}
