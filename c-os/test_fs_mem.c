#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "fs_mem.h"

int main(void) {
    Fs *fs = fs_criar();
    assert(fs && fs_blocos_livres(fs) == FS_NBLOCOS && fs_inodes_livres(fs) == FS_NINODES - 1);
    assert(fs_tipo(fs, "/") == FS_DIR && fs_tipo(fs, "/x") == FS_NADA);

    /* hierarquia basica */
    assert(fs_mkdir(fs, "/etc") == 0 && fs_mkdir(fs, "/etc/conf") == 0);
    assert(fs_criar_arquivo(fs, "/etc/conf/a.txt") == 0);
    assert(fs_tipo(fs, "/etc/conf") == FS_DIR && fs_tipo(fs, "/etc/conf/a.txt") == FS_ARQUIVO);
    assert(fs_tipo(fs, "//etc///conf/") == FS_DIR); /* barras repetidas */
    assert(fs_mkdir(fs, "/etc") == -1);              /* ja existe */
    assert(fs_mkdir(fs, "/nada/sub") == -1);         /* pai inexistente */
    assert(fs_mkdir(fs, "/etc/conf/a.txt/x") == -1); /* pai e arquivo */
    assert(fs_mkdir(fs, "relativo") == -1 && fs_mkdir(fs, "/") == -1);
    assert(fs_mkdir(fs, "/123456789012345678901234567890") == -1); /* nome longo */
    assert(fs_inodes_livres(fs) == FS_NINODES - 4);

    /* escrita/leitura atravessando blocos (300 bytes = 3 blocos de 128) */
    char dados[300], lido[300];
    for (int i = 0; i < 300; i++) dados[i] = (char)('a' + i % 26);
    assert(fs_escrever(fs, "/etc/conf/a.txt", 0, dados, 300) == 300);
    assert(fs_tamanho(fs, "/etc/conf/a.txt") == 300);
    assert(fs_ler(fs, "/etc/conf/a.txt", 0, lido, 300) == 300 && memcmp(dados, lido, 300) == 0);
    /* leitura parcial no meio, cruzando a fronteira do bloco 127/128 */
    char mid[10];
    assert(fs_ler(fs, "/etc/conf/a.txt", 123, mid, 10) == 10 && memcmp(mid, dados + 123, 10) == 0);
    /* leitura alem do fim */
    assert(fs_ler(fs, "/etc/conf/a.txt", 295, lido, 100) == 5);
    assert(fs_ler(fs, "/etc/conf/a.txt", 300, lido, 10) == 0);
    assert(fs_ler(fs, "/etc/conf/a.txt", 999, lido, 10) == 0);

    /* sobrescrita no meio nao altera o tamanho */
    assert(fs_escrever(fs, "/etc/conf/a.txt", 100, "XYZ", 3) == 3);
    assert(fs_tamanho(fs, "/etc/conf/a.txt") == 300);
    assert(fs_ler(fs, "/etc/conf/a.txt", 99, mid, 5) == 5 && memcmp(mid + 1, "XYZ", 3) == 0);

    /* arquivo esparso: escrever no offset 300 em arquivo novo deixa lacuna zerada */
    assert(fs_criar_arquivo(fs, "/esparso") == 0);
    size_t antes = fs_blocos_livres(fs);
    assert(fs_escrever(fs, "/esparso", 300, "Z", 1) == 1);
    assert(fs_blocos_livres(fs) == antes - 1); /* so o bloco 2 foi alocado */
    char esp[301];
    assert(fs_ler(fs, "/esparso", 0, esp, 301) == 301);
    for (int i = 0; i < 300; i++) assert(esp[i] == 0);
    assert(esp[300] == 'Z');

    /* limite de tamanho por arquivo (12 blocos diretos) */
    static char grande[FS_ARQ_MAX + 500];
    memset(grande, 'q', sizeof grande);
    assert(fs_criar_arquivo(fs, "/grande") == 0);
    assert(fs_escrever(fs, "/grande", 0, grande, sizeof grande) == FS_ARQ_MAX);
    assert(fs_escrever(fs, "/grande", FS_ARQ_MAX, "x", 1) == 0);
    assert(fs_tamanho(fs, "/grande") == FS_ARQ_MAX);

    /* operacoes em tipo errado / inexistente */
    assert(fs_escrever(fs, "/etc", 0, "x", 1) == -1 && fs_ler(fs, "/etc", 0, lido, 1) == -1);
    assert(fs_escrever(fs, "/nada", 0, "x", 1) == -1);
    assert(fs_tamanho(fs, "/nada") == -1);

    /* listagem */
    char nomes[8][FS_NOME_TAM];
    assert(fs_listar(fs, "/", nomes, 8) == 3); /* etc, esparso, grande */
    assert(strcmp(nomes[0], "etc") == 0 && strcmp(nomes[1], "esparso") == 0);
    assert(fs_listar(fs, "/etc/conf", nomes, 8) == 1 && strcmp(nomes[0], "a.txt") == 0);
    assert(fs_listar(fs, "/etc/conf/a.txt", nomes, 8) == -1);
    assert(fs_listar(fs, "/", nomes, 2) == 3); /* total mesmo truncando */

    /* remocao: diretorio nao vazio falha; arquivo libera blocos e inode */
    assert(fs_remover(fs, "/etc/conf") == -1 && fs_remover(fs, "/") == -1);
    size_t bl = fs_blocos_livres(fs), il = fs_inodes_livres(fs);
    assert(fs_remover(fs, "/grande") == 0);
    assert(fs_blocos_livres(fs) == bl + FS_DIRETOS && fs_inodes_livres(fs) == il + 1);
    assert(fs_tipo(fs, "/grande") == FS_NADA && fs_remover(fs, "/grande") == -1);
    assert(fs_remover(fs, "/etc/conf/a.txt") == 0 && fs_remover(fs, "/etc/conf") == 0);
    assert(fs_listar(fs, "/", nomes, 8) == 2);
    /* vaga do diretorio e reaproveitada */
    assert(fs_criar_arquivo(fs, "/novo") == 0);
    assert(fs_listar(fs, "/", nomes, 8) == 3);
    fs_destruir(fs);

    /* disco cheio: arquivos de 12 blocos ate nao caber */
    fs = fs_criar();
    assert(fs_mkdir(fs, "/d") == 0);
    int criados = 0;
    char nome[32];
    for (;;) {
        snprintf(nome, sizeof nome, "/d/f%d", criados);
        if (fs_criar_arquivo(fs, nome) < 0) break;
        criados++;
        if (fs_escrever(fs, nome, 0, grande, FS_ARQ_MAX) < FS_ARQ_MAX) break;
    }
    assert(criados >= 18 && criados < 25);
    assert(fs_blocos_livres(fs) < FS_DIRETOS);
    for (int i = 0; i < criados; i++) {
        snprintf(nome, sizeof nome, "/d/f%d", i);
        assert(fs_remover(fs, nome) == 0);
    }
    /* sobram so os blocos dos diretorios ("/" com 1 entrada; "/d" com ceil(criados/4)) */
    assert(fs_blocos_livres(fs) == FS_NBLOCOS - 1 - (size_t)((criados + 3) / 4));
    assert(fs_inodes_livres(fs) == FS_NINODES - 2);
    fs_destruir(fs);

    /* inodes esgotados: criacao falha sem vazar entrada de diretorio */
    fs = fs_criar();
    int n = 0;
    for (;;) {
        snprintf(nome, sizeof nome, "/dir%d", n);
        /* a raiz comporta 48 entradas; com 63 inodes livres o limite e o diretorio */
        if (fs_mkdir(fs, nome) < 0) break;
        n++;
    }
    assert(n == 48 && fs_inodes_livres(fs) == FS_NINODES - 1 - 48);
    fs_destruir(fs);

    puts("test_fs_mem ok");
    return 0;
}
