#include <assert.h>
#include <stdio.h>
#include "vm.h"

int main(void) {
    unsigned char c[256];
    size_t n = 0;
    VM vm;

    /* (2 + 3) * 4 = 20 */
    n = vm_emitir(c, n, OP_PUSH, 2);
    n = vm_emitir(c, n, OP_PUSH, 3);
    n = vm_emitir(c, n, OP_ADD, 0);
    n = vm_emitir(c, n, OP_PUSH, 4);
    n = vm_emitir(c, n, OP_MUL, 0);
    n = vm_emitir(c, n, OP_PRINT, 0);
    n = vm_emitir(c, n, OP_HALT, 0);
    assert(vm_executar(&vm, c, n) == VM_OK);
    assert(vm.n_saida == 1 && vm.saida[0] == 20);

    /* Laco: imprime 3 2 1 (contagem regressiva). */
    n = 0;
    n = vm_emitir(c, n, OP_PUSH, 3);          /* 0  */
    size_t topo = n;
    n = vm_emitir(c, n, OP_DUP, 0);
    size_t jz = n;
    n = vm_emitir(c, n, OP_JZ, 0);            /* remendado abaixo */
    n = vm_emitir(c, n, OP_DUP, 0);
    n = vm_emitir(c, n, OP_PRINT, 0);
    n = vm_emitir(c, n, OP_PUSH, 1);
    n = vm_emitir(c, n, OP_SUB, 0);
    n = vm_emitir(c, n, OP_JMP, (int)topo);
    size_t fim = n;
    n = vm_emitir(c, n, OP_HALT, 0);
    vm_emitir(c, jz, OP_JZ, (int)fim);
    assert(vm_executar(&vm, c, n) == VM_OK);
    assert(vm.n_saida == 3 && vm.saida[0] == 3 && vm.saida[2] == 1);

    /* Erros. */
    n = vm_emitir(c, 0, OP_ADD, 0);
    assert(vm_executar(&vm, c, n) == VM_PILHA_VAZIA);
    n = vm_emitir(c, 0, OP_PUSH, 1);
    n = vm_emitir(c, n, OP_PUSH, 0);
    n = vm_emitir(c, n, OP_DIV, 0);
    assert(vm_executar(&vm, c, n) == VM_DIV_ZERO);
    c[0] = 99;
    assert(vm_executar(&vm, c, 1) == VM_OPCODE_INVALIDO);
    n = vm_emitir(c, 0, OP_PUSH, 1);
    assert(vm_executar(&vm, c, n) == VM_FORA_DO_CODIGO); /* sem HALT */
    n = vm_emitir(c, 0, OP_JMP, 0);
    assert(vm_executar(&vm, c, n) == VM_LIMITE_PASSOS);  /* laco infinito */
    puts("vm ok");
    return 0;
}
