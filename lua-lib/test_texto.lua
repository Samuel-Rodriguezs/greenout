local T = require("texto")

local function igual(a, b)
  if #a ~= #b then return false end
  for i = 1, #a do if a[i] ~= b[i] then return false end end
  return true
end

assert(igual(T.dividir("a,b,c", ","), { "a", "b", "c" }))
assert(igual(T.dividir("", ","), { "" }))
assert(igual(T.dividir("a,,b,", ","), { "a", "", "b", "" }))
assert(igual(T.dividir("a.b.c", "."), { "a", "b", "c" }))        -- separador literal
assert(igual(T.dividir("a--b--c", "--"), { "a", "b", "c" }))
assert(igual(T.dividir("a,b,c,d", ",", 2), { "a", "b,c,d" }))
assert(igual(T.dividir("açb", ""), { "a", "ç", "b" }))

assert(T.aparar("  oi  ") == "oi" and T.aparar("") == "" and T.aparar("   ") == "")
assert(T.aparar("a b") == "a b")
assert(T.aparar_esq("  x ") == "x " and T.aparar_dir("  x ") == "  x")

assert(T.comeca_com("lua", "lu") and not T.comeca_com("lua", "ua") and T.comeca_com("a", ""))
assert(not T.comeca_com("a", "ab"))
assert(T.termina_com("lua", "ua") and not T.termina_com("lua", "lu") and T.termina_com("a", ""))

assert(T.preencher_esq("7", 3, "0") == "007")
assert(T.preencher_esq("1234", 3, "0") == "1234")
assert(T.preencher_dir("ab", 5, ".") == "ab...")
assert(T.preencher_esq("é", 3) == "  é")  -- conta caracteres, não bytes
assert(T.centralizar("ab", 5, "*") == "*ab**")

assert(T.modelo("Olá ${nome}!", { nome = "Ana" }) == "Olá Ana!")
assert(T.modelo("${a.b}-${x}", { a = { b = 1 } }) == "1-")
assert(T.modelo("$${nome}", { nome = "x" }) == "${nome}")
assert(T.modelo("sem marcador", {}) == "sem marcador")
assert(T.modelo("${a.b}", { a = 5 }) == "")

assert(T.capitalizar("lua") == "Lua" and T.capitalizar("") == "" and T.capitalizar("1a") == "1a")
assert(T.contar("abababa", "aba") == 2 and T.contar("abc", "") == 0 and T.contar("a.b.c", ".") == 2)
assert(T.juntar({ 1, "a", true }, "-") == "1-a-true" and T.juntar({}) == "")
print("ok")
