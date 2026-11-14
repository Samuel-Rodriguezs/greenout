#ifndef FAT_H
#define FAT_H

#include <stddef.h>

/* Sistema de arquivos FAT simulado: a tabela de alocacao encadeia os
 * clusters de cada arquivo (valor 0 = livre, -1 = fim de cadeia, outro =
 * proximo cluster). Os clusters sao numerados de 1 a `nclusters`; o
 * diretorio e uma tabela plana de nomes. Nenhum dado e armazenado: so a
 * estrutura de alocacao. */

#define FAT_NOME_MAX 31

typedef struct Fat Fat;

Fat *fat_criar(size_t nclusters, size_t tam_cluster, size_t max_arquivos);
void fat_destruir(Fat *f);

/* Cria um arquivo de `bytes` bytes (0 = sem clusters). Aloca sempre os
 * menores clusters livres. 0 = ok; -1 = nome invalido/duplicado, diretorio
 * cheio ou espaco insuficiente (nada e alterado). */
int fat_criar_arquivo(Fat *f, const char *nome, size_t bytes);
int fat_remover_arquivo(Fat *f, const char *nome);
/* Aumenta o tamanho; so aloca clusters alem da folga do ultimo. */
int fat_estender(Fat *f, const char *nome, size_t bytes_extra);

/* Cluster que contem o byte `offset`, ou -1 (fora do arquivo/inexistente). */
long fat_cluster_de(const Fat *f, const char *nome, size_t offset);
/* Copia a cadeia (ate `max` clusters) e retorna o comprimento total, ou -1. */
long fat_cadeia(const Fat *f, const char *nome, long *saida, size_t max);
/* Numero de trechos contiguos da cadeia (1 = sem fragmentacao, 0 = vazio). */
long fat_fragmentos(const Fat *f, const char *nome);
long fat_tamanho(const Fat *f, const char *nome);

size_t fat_clusters_livres(const Fat *f);
size_t fat_arquivos(const Fat *f);

#endif
