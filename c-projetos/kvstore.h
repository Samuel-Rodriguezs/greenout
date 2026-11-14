#ifndef KVSTORE_H
#define KVSTORE_H
#include <stddef.h>

/* Key-value store em memoria (tabela hash com encadeamento) com
 * persistencia em arquivo texto (uma linha "chave=valor" por entrada). */
typedef struct KVStore KVStore;

KVStore *kv_criar(void);
void kv_liberar(KVStore *kv);
/* Insere ou atualiza. Retorna 0 em sucesso. Chaves nao podem ter '=' ou '\n';
 * valores nao podem ter '\n'. */
int kv_set(KVStore *kv, const char *chave, const char *valor);
/* Retorna o valor (pertence ao store) ou NULL. */
const char *kv_get(const KVStore *kv, const char *chave);
/* Remove; retorna 1 se existia. */
int kv_del(KVStore *kv, const char *chave);
size_t kv_tamanho(const KVStore *kv);
/* Salva/carrega do arquivo. Retornam 0 em sucesso. */
int kv_salvar(const KVStore *kv, const char *caminho);
int kv_carregar(KVStore *kv, const char *caminho);

#endif
