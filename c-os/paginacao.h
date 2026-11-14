#ifndef PAGINACAO_H
#define PAGINACAO_H

#include <stdint.h>

/* Tabela de paginas de dois niveis (estilo x86 de 32 bits sem PAE):
 *   endereco virtual = [dir:10][tabela:10][offset:12]
 * As tabelas de segundo nivel so sao alocadas quando necessarias. */

#define PAG_TAM_PAGINA 4096u

typedef enum { PAG_OK = 0, PAG_FALTA = 1, PAG_PROTECAO = 2 } PagStatus;

typedef struct Paginacao Paginacao;

Paginacao *pag_criar(void);
void pag_destruir(Paginacao *p);

/* Mapeia a pagina virtual `vpn` (20 bits) para `quadro` (20 bits).
 * Remapear sobrescreve. -1 se vpn/quadro excedem 20 bits. */
int pag_mapear(Paginacao *p, uint32_t vpn, uint32_t quadro, int escrita);
/* Remove o mapeamento; 0 se existia, -1 caso contrario. Libera a tabela de
 * segundo nivel quando ela fica vazia. */
int pag_desmapear(Paginacao *p, uint32_t vpn);

/* Traduz um endereco virtual. Em PAG_OK grava o endereco fisico em `*fisico`
 * e marca os bits acessado (e sujo, se escrita). */
PagStatus pag_traduzir(Paginacao *p, uint32_t virt, int escrita, uint32_t *fisico);

int pag_sujo(const Paginacao *p, uint32_t vpn);
int pag_acessado(const Paginacao *p, uint32_t vpn);
/* Numero de tabelas de segundo nivel atualmente alocadas. */
unsigned pag_tabelas_alocadas(const Paginacao *p);

#endif
