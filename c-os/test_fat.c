#include <assert.h>
#include <stdio.h>

#include "fat.h"

int main(void) {
    assert(fat_criar(0, 512, 4) == NULL && fat_criar(4, 0, 4) == NULL);
    Fat *f = fat_criar(10, 512, 4);
    long ch[10];
    assert(f && fat_clusters_livres(f) == 10 && fat_arquivos(f) == 0);

    /* a=2 clusters (1,2), b=2 (3,4), c=2 (5,6) */
    assert(fat_criar_arquivo(f, "a", 1000) == 0); /* ceil(1000/512) = 2 */
    assert(fat_criar_arquivo(f, "b", 1024) == 0);
    assert(fat_criar_arquivo(f, "c", 1025) == 0); /* 1025 bytes -> 3 clusters */
    assert(fat_clusters_livres(f) == 10 - 2 - 2 - 3);
    assert(fat_cadeia(f, "a", ch, 10) == 2 && ch[0] == 1 && ch[1] == 2);
    assert(fat_cadeia(f, "c", ch, 10) == 3 && ch[0] == 5 && ch[2] == 7);
    assert(fat_fragmentos(f, "a") == 1);

    /* traducao de offset em cluster */
    assert(fat_cluster_de(f, "a", 0) == 1 && fat_cluster_de(f, "a", 511) == 1);
    assert(fat_cluster_de(f, "a", 512) == 2 && fat_cluster_de(f, "a", 999) == 2);
    assert(fat_cluster_de(f, "a", 1000) == -1 && fat_cluster_de(f, "z", 0) == -1);

    /* remove b e cria d(3 clusters): ocupa 3,4 e depois 8 -> 2 fragmentos */
    assert(fat_remover_arquivo(f, "b") == 0 && fat_remover_arquivo(f, "b") == -1);
    assert(fat_clusters_livres(f) == 10 - 2 - 3);
    assert(fat_criar_arquivo(f, "d", 1500) == 0);
    assert(fat_cadeia(f, "d", ch, 10) == 3);
    assert(ch[0] == 3 && ch[1] == 4 && ch[2] == 8);
    assert(fat_fragmentos(f, "d") == 2);
    assert(fat_cluster_de(f, "d", 1200) == 8);

    /* diretorio cheio / duplicado / nome invalido */
    assert(fat_criar_arquivo(f, "e", 0) == 0);          /* 4o arquivo: a,c,d,e */
    assert(fat_criar_arquivo(f, "x", 0) == -1);         /* diretorio cheio */
    assert(fat_criar_arquivo(f, "a", 0) == -1);         /* duplicado */
    assert(fat_criar_arquivo(f, "", 0) == -1);
    assert(fat_remover_arquivo(f, "e") == 0);

    /* arquivo vazio e extensao dele */
    assert(fat_criar_arquivo(f, "v", 0) == 0);
    assert(fat_cadeia(f, "v", ch, 10) == 0 && fat_fragmentos(f, "v") == 0);
    assert(fat_cluster_de(f, "v", 0) == -1);
    assert(fat_estender(f, "v", 10) == 0 && fat_cadeia(f, "v", ch, 10) == 1);
    assert(ch[0] == 9);

    /* extensao usa a folga do ultimo cluster antes de alocar outro */
    assert(fat_clusters_livres(f) == 1);                 /* so o cluster 10 */
    assert(fat_estender(f, "v", 502) == 0);              /* 512 bytes: ainda 1 cluster */
    assert(fat_clusters_livres(f) == 1 && fat_tamanho(f, "v") == 512);
    assert(fat_estender(f, "v", 1) == 0);                /* 513: precisa de outro */
    assert(fat_clusters_livres(f) == 0);
    assert(fat_cadeia(f, "v", ch, 10) == 2 && ch[1] == 10);
    assert(fat_fragmentos(f, "v") == 1);                 /* 9 -> 10 contiguo */

    /* sem espaco: nada e alterado */
    assert(fat_estender(f, "v", 600) == -1 && fat_tamanho(f, "v") == 513);
    assert(fat_criar_arquivo(f, "w", 1) == -1 && fat_arquivos(f) == 4);
    assert(fat_estender(f, "nada", 1) == -1);

    /* liberar tudo devolve todos os clusters */
    assert(fat_remover_arquivo(f, "a") == 0 && fat_remover_arquivo(f, "c") == 0);
    assert(fat_remover_arquivo(f, "d") == 0 && fat_remover_arquivo(f, "v") == 0);
    assert(fat_clusters_livres(f) == 10 && fat_arquivos(f) == 0);
    assert(fat_criar_arquivo(f, "tudo", 5120) == 0 && fat_clusters_livres(f) == 0);
    assert(fat_fragmentos(f, "tudo") == 1);
    fat_destruir(f);
    fat_destruir(NULL);

    puts("test_fat ok");
    return 0;
}
