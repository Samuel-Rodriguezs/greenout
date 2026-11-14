#include "fs_mem.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int tipo; /* FS_NADA = inode livre */
    size_t tam;
    int blocos[FS_DIRETOS]; /* -1 = nao alocado (lacuna) */
} Inode;

typedef struct {
    int32_t ino;
    char nome[FS_NOME_TAM]; /* nome[0] == 0: entrada livre */
} DirEnt;

struct Fs {
    unsigned char dados[FS_NBLOCOS][FS_BLOCO];
    unsigned char bloco_usado[FS_NBLOCOS];
    Inode inodes[FS_NINODES];
    size_t blocos_livres;
    size_t inodes_livres;
};

/* ---------- blocos e inodes ---------- */

static int bloco_alocar(Fs *fs) {
    for (int b = 0; b < FS_NBLOCOS; b++)
        if (!fs->bloco_usado[b]) {
            fs->bloco_usado[b] = 1;
            fs->blocos_livres--;
            memset(fs->dados[b], 0, FS_BLOCO);
            return b;
        }
    return -1;
}

static int inode_alocar(Fs *fs, int tipo) {
    for (int i = 0; i < FS_NINODES; i++)
        if (fs->inodes[i].tipo == FS_NADA) {
            Inode *n = &fs->inodes[i];
            n->tipo = tipo;
            n->tam = 0;
            for (int k = 0; k < FS_DIRETOS; k++) n->blocos[k] = -1;
            fs->inodes_livres--;
            return i;
        }
    return -1;
}

static void inode_liberar(Fs *fs, int ino) {
    Inode *n = &fs->inodes[ino];
    for (int k = 0; k < FS_DIRETOS; k++)
        if (n->blocos[k] >= 0) {
            fs->bloco_usado[n->blocos[k]] = 0;
            fs->blocos_livres++;
        }
    n->tipo = FS_NADA;
    fs->inodes_livres++;
}

/* le dentro do tamanho do inode; blocos nao alocados valem zero */
static size_t inode_ler(const Fs *fs, int ino, size_t off, void *buf, size_t n) {
    const Inode *in = &fs->inodes[ino];
    if (off >= in->tam) return 0;
    if (n > in->tam - off) n = in->tam - off;
    unsigned char *dst = buf;
    size_t feitos = 0;
    while (feitos < n) {
        size_t pos = off + feitos, k = pos / FS_BLOCO, d = pos % FS_BLOCO;
        size_t c = FS_BLOCO - d < n - feitos ? FS_BLOCO - d : n - feitos;
        if (in->blocos[k] >= 0) memcpy(dst + feitos, fs->dados[in->blocos[k]] + d, c);
        else memset(dst + feitos, 0, c);
        feitos += c;
    }
    return n;
}

static size_t inode_escrever(Fs *fs, int ino, size_t off, const void *buf, size_t n) {
    Inode *in = &fs->inodes[ino];
    const unsigned char *src = buf;
    size_t feitos = 0;
    while (feitos < n) {
        size_t pos = off + feitos, k = pos / FS_BLOCO, d = pos % FS_BLOCO;
        if (k >= FS_DIRETOS) break;
        if (in->blocos[k] < 0) {
            int b = bloco_alocar(fs);
            if (b < 0) break;
            in->blocos[k] = b;
        }
        size_t c = FS_BLOCO - d < n - feitos ? FS_BLOCO - d : n - feitos;
        memcpy(fs->dados[in->blocos[k]] + d, src + feitos, c);
        feitos += c;
    }
    if (feitos && off + feitos > in->tam) in->tam = off + feitos;
    return feitos;
}

/* ---------- diretorios ---------- */

/* acha a entrada de `nome`; devolve o offset dela no diretorio ou -1 */
static long dir_achar(const Fs *fs, int dir, const char *nome, int32_t *ino) {
    DirEnt e;
    for (size_t off = 0; off < fs->inodes[dir].tam; off += sizeof e) {
        inode_ler(fs, dir, off, &e, sizeof e);
        if (e.nome[0] && strcmp(e.nome, nome) == 0) {
            if (ino) *ino = e.ino;
            return (long)off;
        }
    }
    return -1;
}

static int dir_adicionar(Fs *fs, int dir, const char *nome, int ino) {
    DirEnt e = {0};
    size_t off = 0, fim = fs->inodes[dir].tam;
    for (; off < fim; off += sizeof e) { /* reaproveita vaga livre */
        inode_ler(fs, dir, off, &e, sizeof e);
        if (!e.nome[0]) break;
    }
    memset(&e, 0, sizeof e);
    e.ino = ino;
    strncpy(e.nome, nome, FS_NOME_TAM - 1);
    return inode_escrever(fs, dir, off, &e, sizeof e) == sizeof e ? 0 : -1;
}

static int dir_vazio(const Fs *fs, int dir) {
    DirEnt e;
    for (size_t off = 0; off < fs->inodes[dir].tam; off += sizeof e) {
        inode_ler(fs, dir, off, &e, sizeof e);
        if (e.nome[0]) return 0;
    }
    return 1;
}

/* ---------- caminhos ---------- */

/* Extrai o proximo componente de `*p` em `nome`. 1 = obteve, 0 = fim,
 * -1 = nome longo demais. */
static int componente(const char **p, char *nome) {
    while (**p == '/') (*p)++;
    if (!**p) return 0;
    size_t len = 0;
    while ((*p)[len] && (*p)[len] != '/') len++;
    if (len >= FS_NOME_TAM) return -1;
    memcpy(nome, *p, len);
    nome[len] = '\0';
    *p += len;
    return 1;
}

/* Resolve `caminho`. Com `pai` != NULL para no penultimo componente: devolve
 * o inode do diretorio pai e o ultimo componente em `ultimo` (a raiz nao tem
 * ultimo: erro). Sem `pai`, devolve o inode do alvo. -1 em falha. */
static int resolver(const Fs *fs, const char *caminho, int pai, char *ultimo) {
    if (!caminho || caminho[0] != '/') return -1;
    const char *p = caminho;
    int atual = 0;
    char nome[FS_NOME_TAM];
    int r = componente(&p, nome);
    if (r < 0) return -1;
    if (r == 0) return pai ? -1 : 0; /* "/" */
    for (;;) {
        char prox[FS_NOME_TAM];
        const char *q = p;
        int r2 = componente(&q, prox);
        if (r2 < 0) return -1;
        if (r2 == 0) { /* `nome` e o ultimo componente */
            if (pai) {
                if (fs->inodes[atual].tipo != FS_DIR) return -1;
                strcpy(ultimo, nome);
                return atual;
            }
        }
        if (fs->inodes[atual].tipo != FS_DIR) return -1;
        int32_t ino;
        if (dir_achar(fs, atual, nome, &ino) < 0) return -1;
        atual = ino;
        if (r2 == 0) return atual;
        strcpy(nome, prox);
        p = q;
    }
}

/* ---------- API ---------- */

Fs *fs_criar(void) {
    Fs *fs = calloc(1, sizeof *fs);
    if (!fs) return NULL;
    fs->blocos_livres = FS_NBLOCOS;
    fs->inodes_livres = FS_NINODES;
    inode_alocar(fs, FS_DIR); /* inode 0 = raiz */
    return fs;
}

void fs_destruir(Fs *fs) { free(fs); }

static int criar_no(Fs *fs, const char *caminho, int tipo) {
    char nome[FS_NOME_TAM];
    int pai = resolver(fs, caminho, 1, nome);
    if (pai < 0 || dir_achar(fs, pai, nome, NULL) >= 0) return -1;
    int ino = inode_alocar(fs, tipo);
    if (ino < 0) return -1;
    if (dir_adicionar(fs, pai, nome, ino) < 0) {
        inode_liberar(fs, ino); /* desfaz: sem espaco para a entrada */
        return -1;
    }
    return 0;
}

int fs_mkdir(Fs *fs, const char *caminho) { return criar_no(fs, caminho, FS_DIR); }
int fs_criar_arquivo(Fs *fs, const char *caminho) { return criar_no(fs, caminho, FS_ARQUIVO); }

int fs_remover(Fs *fs, const char *caminho) {
    char nome[FS_NOME_TAM];
    int pai = resolver(fs, caminho, 1, nome);
    if (pai < 0) return -1;
    int32_t ino;
    long off = dir_achar(fs, pai, nome, &ino);
    if (off < 0) return -1;
    if (fs->inodes[ino].tipo == FS_DIR && !dir_vazio(fs, ino)) return -1;
    DirEnt vazio = {0};
    inode_escrever(fs, pai, (size_t)off, &vazio, sizeof vazio);
    inode_liberar(fs, ino);
    return 0;
}

long fs_escrever(Fs *fs, const char *caminho, size_t off, const void *buf, size_t n) {
    int ino = resolver(fs, caminho, 0, NULL);
    if (ino < 0 || fs->inodes[ino].tipo != FS_ARQUIVO) return -1;
    return (long)inode_escrever(fs, ino, off, buf, n);
}

long fs_ler(const Fs *fs, const char *caminho, size_t off, void *buf, size_t n) {
    int ino = resolver(fs, caminho, 0, NULL);
    if (ino < 0 || fs->inodes[ino].tipo != FS_ARQUIVO) return -1;
    return (long)inode_ler(fs, ino, off, buf, n);
}

int fs_tipo(const Fs *fs, const char *caminho) {
    int ino = resolver(fs, caminho, 0, NULL);
    return ino < 0 ? FS_NADA : fs->inodes[ino].tipo;
}

long fs_tamanho(const Fs *fs, const char *caminho) {
    int ino = resolver(fs, caminho, 0, NULL);
    return ino < 0 ? -1 : (long)fs->inodes[ino].tam;
}

long fs_listar(const Fs *fs, const char *caminho, char (*nomes)[FS_NOME_TAM], size_t max) {
    int ino = resolver(fs, caminho, 0, NULL);
    if (ino < 0 || fs->inodes[ino].tipo != FS_DIR) return -1;
    long total = 0;
    DirEnt e;
    for (size_t off = 0; off < fs->inodes[ino].tam; off += sizeof e) {
        inode_ler(fs, ino, off, &e, sizeof e);
        if (!e.nome[0]) continue;
        if ((size_t)total < max) memcpy(nomes[total], e.nome, FS_NOME_TAM);
        total++;
    }
    return total;
}

size_t fs_blocos_livres(const Fs *fs) { return fs->blocos_livres; }
size_t fs_inodes_livres(const Fs *fs) { return fs->inodes_livres; }
