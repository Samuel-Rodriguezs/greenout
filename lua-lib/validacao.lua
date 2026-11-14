-- Validação de dados contra esquemas declarativos.
--   tipo: "string"|"numero"|"inteiro"|"booleano"|"tabela"|"lista"|"funcao"|"qualquer"
--   obrigatorio, min, max (valor, tamanho de string ou de lista), padrao (padrão Lua),
--   enum, campos (tabela), estrito (rejeita campos extras), itens (esquema da lista),
--   validador (função(valor) -> true | false, mensagem)
local M = {}

local function eh_lista(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  return n == #t
end

local verificadores = {
  string = function(v) return type(v) == "string" end,
  numero = function(v) return type(v) == "number" and v == v end,
  inteiro = function(v) return math.type(v) == "integer" end,
  booleano = function(v) return type(v) == "boolean" end,
  tabela = function(v) return type(v) == "table" end,
  lista = function(v) return type(v) == "table" and eh_lista(v) end,
  funcao = function(v) return type(v) == "function" end,
  qualquer = function() return true end,
}

local function tamanho_de(v, tipo)
  if type(v) == "string" then return #v end
  if tipo == "lista" then return #v end
  return v
end

local function validar_no(valor, esq, caminho, erros)
  local function erro(msg) erros[#erros + 1] = caminho .. ": " .. msg end

  if valor == nil then
    if esq.obrigatorio then erro("campo obrigatorio") end
    return
  end

  local tipo = esq.tipo or "qualquer"
  local verif = verificadores[tipo]
  if not verif then error("tipo de esquema desconhecido: " .. tostring(tipo), 0) end
  if not verif(valor) then
    erro("esperado " .. tipo .. ", recebido " .. (type(valor) == "table" and "tabela" or type(valor)))
    return
  end

  if esq.min or esq.max then
    if type(valor) == "number" or type(valor) == "string" or tipo == "lista" then
      local t = tamanho_de(valor, tipo)
      local unidade = type(valor) == "number" and "valor" or "tamanho"
      if esq.min and t < esq.min then erro(unidade .. " menor que o minimo " .. esq.min) end
      if esq.max and t > esq.max then erro(unidade .. " maior que o maximo " .. esq.max) end
    end
  end

  if esq.padrao and type(valor) == "string" and not valor:find(esq.padrao) then
    erro("nao corresponde ao padrao")
  end

  if esq.enum then
    local achou = false
    for _, e in ipairs(esq.enum) do if e == valor then achou = true break end end
    if not achou then erro("valor fora do conjunto permitido") end
  end

  if esq.validador then
    local ok, msg = esq.validador(valor)
    if not ok then erro(msg or "validador personalizado falhou") end
  end

  if tipo == "lista" and esq.itens then
    for i, item in ipairs(valor) do
      validar_no(item, esq.itens, caminho .. "[" .. i .. "]", erros)
    end
  end

  if type(valor) == "table" and esq.campos then
    local nomes = {}
    for nome in pairs(esq.campos) do nomes[#nomes + 1] = nome end
    table.sort(nomes)
    for _, nome in ipairs(nomes) do
      local sub = caminho == "$" and ("$." .. nome) or (caminho .. "." .. nome)
      validar_no(valor[nome], esq.campos[nome], sub, erros)
    end
    if esq.estrito then
      local extras = {}
      for k in pairs(valor) do
        if esq.campos[k] == nil then extras[#extras + 1] = tostring(k) end
      end
      table.sort(extras)
      for _, k in ipairs(extras) do erro("campo nao permitido '" .. k .. "'") end
    end
  end
end

-- Retorna true, {} se válido; ou false, lista de mensagens de erro.
function M.validar(valor, esquema)
  local erros = {}
  validar_no(valor, esquema, "$", erros)
  return #erros == 0, erros
end

return M
