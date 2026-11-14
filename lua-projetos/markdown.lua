-- Conversor Markdown simples -> HTML.
-- Suporta: títulos (#..######), parágrafos, **negrito**, *itálico*, `código`,
-- [links](url), listas com "- " ou "* " e numeradas "1. ", blocos ``` e citações "> ".
local M = {}

local function escapar(s)
  return (s:gsub("[&<>]", { ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;" }))
end
M.escapar = escapar

-- Formatação em linha. Trechos de código são protegidos antes das demais regras.
local function inline(s)
  s = escapar(s)
  local codigos = {}
  s = s:gsub("`([^`]+)`", function(c)
    codigos[#codigos + 1] = "<code>" .. c .. "</code>"
    return "\0" .. #codigos .. "\0"
  end)
  s = s:gsub("%[([^%]]+)%]%(([^%)]+)%)", '<a href="%2">%1</a>')
  s = s:gsub("%*%*([^%*]+)%*%*", "<strong>%1</strong>")
  s = s:gsub("%*([^%*]+)%*", "<em>%1</em>")
  s = s:gsub("%z(%d+)%z", function(i) return codigos[tonumber(i)] end)
  return s
end
M.inline = inline

function M.converter(texto)
  local saida = {}
  local linhas = {}
  for l in (texto .. "\n"):gmatch("(.-)\r?\n") do linhas[#linhas + 1] = l end

  local i, n = 1, #linhas
  while i <= n do
    local l = linhas[i]
    if l:match("^```") then
      local bloco = {}
      i = i + 1
      while i <= n and not linhas[i]:match("^```") do
        bloco[#bloco + 1] = escapar(linhas[i])
        i = i + 1
      end
      i = i + 1 -- fecha (ou fim do texto)
      saida[#saida + 1] = "<pre><code>" .. table.concat(bloco, "\n") .. "</code></pre>"
    elseif l:match("^%s*$") then
      i = i + 1
    elseif l:match("^#+ ") and #l:match("^#+") <= 6 then
      local marcas, resto = l:match("^(#+) (.*)$")
      saida[#saida + 1] = string.format("<h%d>%s</h%d>", #marcas, inline(resto), #marcas)
      i = i + 1
    elseif l:match("^[%-%*] ") or l:match("^%d+%. ") then
      local ordenada = l:match("^%d+%. ") ~= nil
      local itens = {}
      while i <= n do
        local item = ordenada and linhas[i]:match("^%d+%. (.*)$")
          or (not ordenada and linhas[i]:match("^[%-%*] (.*)$"))
        if not item then break end
        itens[#itens + 1] = "<li>" .. inline(item) .. "</li>"
        i = i + 1
      end
      local tag = ordenada and "ol" or "ul"
      saida[#saida + 1] = "<" .. tag .. ">" .. table.concat(itens) .. "</" .. tag .. ">"
    elseif l:match("^> ?") then
      local q = {}
      while i <= n and linhas[i]:match("^> ?") do
        q[#q + 1] = linhas[i]:gsub("^> ?", "")
        i = i + 1
      end
      saida[#saida + 1] = "<blockquote>" .. inline(table.concat(q, " ")) .. "</blockquote>"
    else
      -- a primeira linha sempre entra (evita laço infinito com "####### x")
      local p = { l }
      i = i + 1
      while i <= n and not linhas[i]:match("^%s*$") and not linhas[i]:match("^#+ ")
        and not linhas[i]:match("^```") and not linhas[i]:match("^[%-%*] ")
        and not linhas[i]:match("^%d+%. ") and not linhas[i]:match("^>") do
        p[#p + 1] = linhas[i]
        i = i + 1
      end
      saida[#saida + 1] = "<p>" .. inline(table.concat(p, " ")) .. "</p>"
    end
  end
  return table.concat(saida, "\n")
end

return M
