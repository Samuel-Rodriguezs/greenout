#ifndef FS_MEM_H
#define FS_MEM_H

#include <stddef.h>

/* Sistema de arquivos em memoria no estilo Unix simplificado: superbloco
 * implicito, tabela de inodes, bitmap de blocos e diretorios armazenados
 * como arquivos de entradas de 32 bytes. Caminhos sao absolutos ("/a/b");
 * nao ha "." nem "..". Cada inode tem ate FS_DIRETOS blocos diretos. */

#define FS_BLOCO 128
#define FS_NBLOCOS 256
#define FS_NINODES 64
#define FS_DIRETOS 12
#define FS_NOME_TAM 28 /* 27 caracteres + '\0' */
#define FS_ARQ_MAX (FS_BLOCO * FS_DIRETOS)

enum { FS_NADA = 0, FS_ARQUIVO = 1, FS_DIR = 2 };

typedef struct Fs Fs;

Fs *fs_criar(void);
void fs_destruir(Fs *fs);

int fs_mkdir(Fs *fs, const char *caminho);
int fs_criar_arquivo(Fs *fs, const char *caminho);
/* Remove arquivo ou diretorio vazio (nunca a raiz). */
int fs_remover(Fs *fs, const char *caminho);

/* Escreve `n` bytes a partir de `off` (estende o arquivo; lacunas leem como
 * zero). Retorna os bytes escritos (pode ser < n se o disco encher ou o
 * limite FS_ARQ_MAX for atingido) ou -1 em erro. */
long fs_escrever(Fs *fs, const char *caminho, size_t off, const void *buf, size_t n);
/* Le ate `n` bytes; retorna os bytes lidos (0 no fim do arquivo) ou -1. */
long fs_ler(const Fs *fs, const char *caminho, size_t off, void *buf, size_t n);

int fs_tipo(const Fs *fs, const char *caminho);
long fs_tamanho(const Fs *fs, const char *caminho);
/* Lista os nomes de um diretorio (ordem de criacao/reuso de vagas); retorna
 * a quantidade total ou -1. Grava no maximo `max` nomes. */
long fs_listar(const Fs *fs, const char *caminho, char (*nomes)[FS_NOME_TAM], size_t max);

size_t fs_blocos_livres(const Fs *fs);
size_t fs_inodes_livres(const Fs *fs);

#endif
