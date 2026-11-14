-- Iteradores e geradores preguiçosos com coroutines.
-- Todos retornam funções iteradoras utilizáveis em `for x in ... do`.
local M = {}

-- Gera um iterador a partir de uma função produtora que chama `emitir(v)`.
function M.gerador(produtor, ...)
  local args = table.pack(...)
  local co = coroutine.wrap(function()
    produtor(coroutine.yield, table.unpack(args, 1, args.n))
  end)
  return co
end

-- inicio..fim (inclusive) com passo; passo 0 é inválido.
function M.faixa(inicio, fim, passo)
  passo = passo or 1
  assert(passo ~= 0, "passo não pode ser zero")
  return M.gerador(function(emitir)
    for i = inicio, fim, passo do emitir(i) end
  end)
end

-- Iterador infinito 0,1,1,2,3,5...
function M.fibonacci()
  return M.gerador(function(emitir)
    local a, b = 0, 1
    while true do
      emitir(a)
      a, b = b, a + b
    end
  end)
end

-- Aplica fn a cada elemento.
function M.mapear(it, fn)
  return M.gerador(function(emitir)
    for v in it do emitir(fn(v)) end
  end)
end

function M.filtrar(it, pred)
  return M.gerador(function(emitir)
    for v in it do if pred(v) then emitir(v) end end
  end)
end

-- Primeiros n elementos (sem consumir além do necessário).
function M.pegar(it, n)
  return M.gerador(function(emitir)
    if n <= 0 then return end
    local i = 0
    for v in it do
      emitir(v)
      i = i + 1
      if i >= n then return end
    end
  end)
end

-- Pares {a, b} dos dois iteradores; termina quando o menor acabar.
function M.zip(it1, it2)
  return M.gerador(function(emitir)
    while true do
      local a, b = it1(), it2()
      if a == nil or b == nil then return end
      emitir({ a, b })
    end
  end)
end

-- Percorre uma árvore {valor=, filhos={...}} em ordem (pré-ordem).
function M.arvore(no)
  return M.gerador(function(emitir)
    local function visitar(n)
      emitir(n.valor)
      for _, f in ipairs(n.filhos or {}) do visitar(f) end
    end
    if no then visitar(no) end
  end)
end

-- Permutações de uma lista (algoritmo recursivo; cada uma é uma cópia).
function M.permutacoes(lista)
  return M.gerador(function(emitir)
    local function perm(a, n)
      if n <= 1 then
        emitir({ table.unpack(a) })
      else
        for i = 1, n do
          a[i], a[n] = a[n], a[i]
          perm(a, n - 1)
          a[i], a[n] = a[n], a[i]
        end
      end
    end
    perm({ table.unpack(lista) }, #lista)
  end)
end

-- Coleta tudo em uma lista.
function M.lista(it)
  local r = {}
  for v in it do r[#r + 1] = v end
  return r
end

return M
