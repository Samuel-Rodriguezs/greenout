-- Utilitários de programação funcional sobre listas e funções.
local M = {}

function M.mapear(lista, f)
  local r = {}
  for i = 1, #lista do r[i] = f(lista[i], i) end
  return r
end

function M.filtrar(lista, pred)
  local r = {}
  for i = 1, #lista do
    if pred(lista[i], i) then r[#r + 1] = lista[i] end
  end
  return r
end

-- Sem valor inicial usa o primeiro elemento; lista vazia sem inicial é erro.
function M.reduzir(lista, f, inicial)
  local acc, ini = inicial, 1
  if inicial == nil then
    if #lista == 0 then error("reduzir de lista vazia sem valor inicial", 2) end
    acc, ini = lista[1], 2
  end
  for i = ini, #lista do acc = f(acc, lista[i], i) end
  return acc
end

-- compor(f, g, h)(x) == f(g(h(x)))
function M.compor(...)
  local fs = { ... }
  local n = #fs
  if n == 0 then return function(...) return ... end end
  return function(...)
    local r = table.pack(fs[n](...))
    for i = n - 1, 1, -1 do r = table.pack(fs[i](table.unpack(r, 1, r.n))) end
    return table.unpack(r, 1, r.n)
  end
end

-- encadear(f, g, h)(x) == h(g(f(x)))
function M.encadear(...)
  local fs = { ... }
  local n = #fs
  local ordem = {}
  for i = 1, n do ordem[i] = fs[n - i + 1] end
  return M.compor(table.unpack(ordem))
end

-- Currying; `aridade` padrão vem da quantidade de parâmetros declarados.
function M.curry(f, aridade)
  aridade = aridade or debug.getinfo(f, "u").nparams
  local function acumular(acc, na)
    return function(...)
      local novo = table.pack(...)
      local todos = { table.unpack(acc, 1, na) }
      for i = 1, novo.n do todos[na + i] = novo[i] end
      local total = na + novo.n
      if total >= aridade then return f(table.unpack(todos, 1, total)) end
      return acumular(todos, total)
    end
  end
  return acumular({}, 0)
end

-- Aplicação parcial à esquerda.
function M.parcial(f, ...)
  local fixos = table.pack(...)
  return function(...)
    local novo = table.pack(...)
    local args = { table.unpack(fixos, 1, fixos.n) }
    for i = 1, novo.n do args[fixos.n + i] = novo[i] end
    return f(table.unpack(args, 1, fixos.n + novo.n))
  end
end

function M.intervalo(ini, fim, passo)
  passo = passo or 1
  if passo == 0 then error("passo zero", 2) end
  local r = {}
  for i = ini, fim, passo do r[#r + 1] = i end
  return r
end

function M.zip(a, b)
  local r = {}
  for i = 1, math.min(#a, #b) do r[i] = { a[i], b[i] } end
  return r
end

function M.algum(lista, pred)
  for i = 1, #lista do if pred(lista[i]) then return true end end
  return false
end

function M.todos(lista, pred)
  for i = 1, #lista do if not pred(lista[i]) then return false end end
  return true
end

function M.achatar(lista)
  local r = {}
  for _, v in ipairs(lista) do
    if type(v) == "table" then
      for _, x in ipairs(M.achatar(v)) do r[#r + 1] = x end
    else
      r[#r + 1] = v
    end
  end
  return r
end

return M
