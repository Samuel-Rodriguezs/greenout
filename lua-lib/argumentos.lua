-- Parser de argumentos de linha de comando.
-- opcoes = { nome = { tipo = "booleano"|"texto"|"numero", curto = "n", padrao = ..., repetivel = bool } }
-- Suporta --nome=valor, --nome valor, -n valor, -abc (flags agrupadas), "--" (fim das opções).
local M = {}

local function converter(def, nome, bruto)
  if def.tipo == "numero" then
    local n = tonumber(bruto)
    if not n then return nil, "valor invalido para --" .. nome .. ": " .. bruto end
    return n
  elseif def.tipo == "booleano" then
    if bruto == "true" then return true end
    if bruto == "false" then return false end
    return nil, "valor invalido para --" .. nome .. ": " .. bruto
  end
  return bruto
end

-- Devolve { opcoes = {...}, posicionais = {...} } ou nil, mensagem de erro.
function M.analisar(args, opcoes)
  opcoes = opcoes or {}
  local curtos = {}
  for nome, def in pairs(opcoes) do
    if def.curto then curtos[def.curto] = nome end
  end

  local res = { opcoes = {}, posicionais = {} }
  for nome, def in pairs(opcoes) do
    if def.padrao ~= nil then res.opcoes[nome] = def.padrao end
  end

  local function guardar(nome, def, valor)
    if def.repetivel then
      local l = res.opcoes[nome]
      if type(l) ~= "table" or l._padrao then l = {}; res.opcoes[nome] = l end
      l[#l + 1] = valor
    else
      res.opcoes[nome] = valor
    end
  end

  local i, n = 1, #args
  while i <= n do
    local a = args[i]
    if a == "--" then
      for j = i + 1, n do res.posicionais[#res.posicionais + 1] = args[j] end
      break
    elseif a:sub(1, 2) == "--" then
      local nome, valor = a:match("^%-%-([^=]+)=(.*)$")
      nome = nome or a:sub(3)
      local def = opcoes[nome]
      if not def then return nil, "opcao desconhecida: --" .. nome end
      if def.tipo == "booleano" then
        if valor ~= nil then
          local v, err = converter(def, nome, valor)
          if v == nil then return nil, err end
          guardar(nome, def, v)
        else
          guardar(nome, def, true)
        end
      else
        if valor == nil then
          i = i + 1
          valor = args[i]
          if valor == nil then return nil, "opcao --" .. nome .. " requer um valor" end
        end
        local v, err = converter(def, nome, valor)
        if v == nil then return nil, err end
        guardar(nome, def, v)
      end
    elseif a:sub(1, 1) == "-" and #a > 1 and not tonumber(a) then
      local letras = a:sub(2)
      for k = 1, #letras do
        local l = letras:sub(k, k)
        local nome = curtos[l]
        if not nome then return nil, "opcao desconhecida: -" .. l end
        local def = opcoes[nome]
        if def.tipo == "booleano" then
          guardar(nome, def, true)
        else
          -- opção com valor: resto do grupo (-n5) ou próximo argumento
          local valor = letras:sub(k + 1)
          if valor == "" then
            i = i + 1
            valor = args[i]
            if valor == nil then return nil, "opcao -" .. l .. " requer um valor" end
          end
          local v, err = converter(def, nome, valor)
          if v == nil then return nil, err end
          guardar(nome, def, v)
          break
        end
      end
    else
      res.posicionais[#res.posicionais + 1] = a
    end
    i = i + 1
  end
  return res
end

-- Gera texto de ajuda ordenado por nome.
function M.ajuda(opcoes)
  local nomes = {}
  for nome in pairs(opcoes) do nomes[#nomes + 1] = nome end
  table.sort(nomes)
  local linhas = {}
  for _, nome in ipairs(nomes) do
    local d = opcoes[nome]
    local s = "  " .. (d.curto and ("-" .. d.curto .. ", ") or "    ") .. "--" .. nome
    if d.tipo and d.tipo ~= "booleano" then s = s .. " <" .. d.tipo .. ">" end
    if d.descricao then s = s .. "  " .. d.descricao end
    linhas[#linhas + 1] = s
  end
  return table.concat(linhas, "\n")
end

return M
