#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "disco_sched.h"

static int igual(const int *a, const int *b, size_t n) {
    return memcmp(a, b, n * sizeof(int)) == 0;
}

int main(void) {
    /* exemplo de Silberschatz: disco 0..199, cabeca em 53 */
    int req[] = {98, 183, 37, 122, 14, 124, 65, 67};
    size_t n = 8;
    int o[8];

    assert(disco_fcfs(53, req, n, 199, o) == 640);
    assert(igual(o, req, n));

    int sstf[] = {65, 67, 37, 14, 98, 122, 124, 183};
    assert(disco_sstf(53, req, n, 199, o) == 236);
    assert(igual(o, sstf, n));

    /* SCAN subindo: 53->199 (146), volta ate 14 (185): 331 */
    int scan_up[] = {65, 67, 98, 122, 124, 183, 37, 14};
    assert(disco_scan(53, req, n, 199, 1, o) == 331);
    assert(igual(o, scan_up, n));

    /* SCAN descendo: 53->0 (53) e sobe ate 183: 53 + 183 = 236 */
    int scan_dn[] = {37, 14, 65, 67, 98, 122, 124, 183};
    assert(disco_scan(53, req, n, 199, 0, o) == 236);
    assert(igual(o, scan_dn, n));

    /* C-SCAN subindo: 146 + salto 199 + 37 sobe ate 37 = 382 (conta o salto) */
    int cs_up[] = {65, 67, 98, 122, 124, 183, 14, 37};
    assert(disco_cscan(53, req, n, 199, 1, o) == 146 + 199 + 37);
    assert(igual(o, cs_up, n));

    /* C-SCAN descendo: 53 + 199 + (199-65) = 386 */
    int cs_dn[] = {37, 14, 183, 124, 122, 98, 67, 65};
    assert(disco_cscan(53, req, n, 199, 0, o) == 386);
    assert(igual(o, cs_dn, n));

    /* so pedidos de um lado: SCAN subindo nao volta; C-SCAN nao salta */
    int alto[] = {60, 80};
    assert(disco_scan(50, alto, 2, 100, 1, NULL) == 50);
    assert(disco_cscan(50, alto, 2, 100, 1, NULL) == 50);
    /* subindo mas so ha pedidos abaixo: vai a borda, volta ate o menor */
    int baixo[] = {10, 30};
    assert(disco_scan(50, baixo, 2, 100, 1, o) == 50 + 90);
    assert(o[0] == 30 && o[1] == 10);
    assert(disco_cscan(50, baixo, 2, 100, 1, o) == 50 + 100 + 30);
    assert(o[0] == 10 && o[1] == 30);

    /* pedido exatamente na cabeca custa zero */
    int aqui[] = {50};
    assert(disco_fcfs(50, aqui, 1, 100, NULL) == 0);
    assert(disco_sstf(50, aqui, 1, 100, NULL) == 0);
    assert(disco_scan(50, aqui, 1, 100, 0, o) == 50 && o[0] == 50);

    /* duplicados e lista vazia */
    int dup[] = {20, 20, 20};
    assert(disco_sstf(10, dup, 3, 50, NULL) == 10);
    assert(disco_fcfs(7, NULL, 0, 50, NULL) == 0);
    assert(disco_sstf(7, NULL, 0, 50, NULL) == 0);
    assert(disco_scan(7, NULL, 0, 50, 1, NULL) == 0);
    assert(disco_cscan(7, NULL, 0, 50, 0, NULL) == 0);

    /* fora do intervalo */
    int ruim[] = {5, 300};
    assert(disco_fcfs(10, ruim, 2, 199, NULL) == -1);
    assert(disco_sstf(10, ruim, 2, 199, NULL) == -1);
    assert(disco_scan(10, ruim, 2, 199, 1, NULL) == -1);
    assert(disco_cscan(10, ruim, 2, 199, 1, NULL) == -1);
    assert(disco_fcfs(-1, req, n, 199, NULL) == -1);
    assert(disco_fcfs(200, req, n, 199, NULL) == -1);

    /* SSTF nunca perde para FCFS neste exemplo e atende todos os pedidos */
    assert(disco_sstf(53, req, n, 199, NULL) < disco_fcfs(53, req, n, 199, NULL));

    puts("test_disco_sched ok");
    return 0;
}
