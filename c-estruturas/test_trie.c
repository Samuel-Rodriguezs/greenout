#include <assert.h>
#include <stdio.h>
#include "trie.h"

int main(void) {
    Trie *t = trie_nova();
    assert(trie_tam(t) == 0);
    assert(!trie_contem(t, "a") && !trie_tem_prefixo(t, "a"));
    assert(trie_tem_prefixo(t, ""));               /* prefixo vazio sempre existe */
    assert(!trie_contem(t, ""));
    assert(trie_inserir(t, "casa") && trie_inserir(t, "casamento") && trie_inserir(t, "cabo"));
    assert(!trie_inserir(t, "casa"));              /* duplicata */
    assert(trie_tam(t) == 3);
    assert(trie_contem(t, "casa") && trie_contem(t, "cabo"));
    assert(!trie_contem(t, "cas") && !trie_contem(t, "casas"));
    assert(trie_tem_prefixo(t, "cas") && !trie_tem_prefixo(t, "cax"));
    assert(trie_conta_prefixo(t, "ca") == 3);
    assert(trie_conta_prefixo(t, "casa") == 2);
    assert(trie_conta_prefixo(t, "z") == 0);
    assert(trie_conta_prefixo(t, "") == 3);

    assert(trie_inserir(t, ""));                   /* palavra vazia */
    assert(trie_contem(t, "") && trie_tam(t) == 4);
    assert(trie_remover(t, ""));
    assert(!trie_contem(t, ""));

    assert(trie_remover(t, "casa"));               /* prefixo de outra: mantem o ramo */
    assert(!trie_contem(t, "casa") && trie_contem(t, "casamento"));
    assert(trie_tem_prefixo(t, "casa"));
    assert(!trie_remover(t, "casa"));
    assert(trie_remover(t, "casamento"));          /* poda o ramo */
    assert(!trie_tem_prefixo(t, "cas") && trie_tem_prefixo(t, "cab"));
    assert(trie_conta_prefixo(t, "ca") == 1 && trie_tam(t) == 1);

    /* bytes fora do ASCII baixo */
    assert(trie_inserir(t, "a\xc3\xa7\xc3\xa3o") && trie_contem(t, "a\xc3\xa7\xc3\xa3o"));
    trie_liberar(t);                               /* libera com palavras restantes */
    trie_liberar(NULL);
    puts("trie ok");
    return 0;
}
