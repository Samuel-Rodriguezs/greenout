local b64 = require("base64")

-- vetores da RFC 4648
local casos = {
  { "", "" }, { "f", "Zg==" }, { "fo", "Zm8=" }, { "foo", "Zm9v" },
  { "foob", "Zm9vYg==" }, { "fooba", "Zm9vYmE=" }, { "foobar", "Zm9vYmFy" },
}
for _, c in ipairs(casos) do
  assert(b64.codificar(c[1]) == c[2], c[1])
  assert(b64.decodificar(c[2]) == c[1], c[2])
end

-- bytes arbitrários e ida-e-volta de todos os valores
local todos = {}
for i = 0, 255 do todos[#todos + 1] = string.char(i) end
todos = table.concat(todos)
assert(b64.decodificar(b64.codificar(todos)) == todos)
assert(b64.codificar("\255\255\255") == "////")
assert(b64.codificar("\0") == "AA==")

-- UTF-8
assert(b64.decodificar(b64.codificar("olá, ção")) == "olá, ção")

-- URL-safe e sem padding
assert(b64.codificar("\251\255", { url = true }) == "-_8=")
assert(b64.codificar("\251\255") == "+/8=")
assert(b64.codificar("f", { sem_padding = true }) == "Zg")
assert(b64.decodificar("Zg") == "f" and b64.decodificar("Zm8") == "fo")
assert(b64.decodificar("-_8=", { url = true }) == "\251\255")
assert(b64.decodificar(b64.codificar(todos, { url = true, sem_padding = true }), { url = true }) == todos)
assert(b64.decodificar("-_8", { url = false }) == nil)    -- alfabeto errado

-- espaços ignorados
assert(b64.decodificar("Zm9v\nYmFy ") == "foobar")

-- entradas inválidas
local r, e = b64.decodificar("Zm9!")
assert(r == nil and e:find("caractere invalido"))
assert(select(2, b64.decodificar("Z")) == "tamanho invalido")
assert(select(2, b64.decodificar("Zg=a")) == "padding no meio do texto")
assert(select(2, b64.decodificar("Zg===")) == "padding excessivo")
assert(select(2, b64.decodificar("Zm9=Zm8=")) ~= nil)
assert(select(2, b64.decodificar("Zm8==")) == "padding incorreto")

-- entrada grande
local grande = string.rep("abc123", 10000)
assert(b64.decodificar(b64.codificar(grande)) == grande)
print("ok")
