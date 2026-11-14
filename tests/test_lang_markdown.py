import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_markdown import ErroMarkdown, tokenizar, tokens_inline

DOC = """# Título principal

Um parágrafo com **negrito**, *itálico* e `código`.
Continua na linha seguinte.

## Lista

- item um
  - sub item
* outro
1. primeiro
2) segundo

> citação [link](http://x.com)

---

```python
def f():
    # não é título
    return 1
```
"""


class TestMarkdown(unittest.TestCase):
    def test_tipos_em_ordem(self):
        tipos = [t.tipo for t in tokenizar(DOC)]
        self.assertEqual(tipos, ["titulo", "paragrafo", "titulo", "item", "item", "item", "item_numerado",
                                 "item_numerado", "citacao", "regra", "codigo"])

    def test_titulos(self):
        t = tokenizar("# A\n###### B ##")
        self.assertEqual([(x.nivel, x.texto) for x in t], [(1, "A"), (6, "B")])

    def test_paragrafo_unido(self):
        t = tokenizar(DOC)[1]
        self.assertIn("Continua na linha seguinte.", t.texto)
        self.assertEqual([k for k, _ in t.inline if k != "texto"], ["negrito", "italico", "codigo"])

    def test_niveis_de_item(self):
        itens = [t for t in tokenizar(DOC) if t.tipo == "item"]
        self.assertEqual([i.nivel for i in itens], [0, 1, 0])

    def test_codigo_preserva_conteudo(self):
        c = tokenizar(DOC)[-1]
        self.assertEqual(c.linguagem, "python")
        self.assertEqual(c.texto, "def f():\n    # não é título\n    return 1")

    def test_inline(self):
        self.assertEqual(
            tokens_inline("a **b** c [x](u) ![i](p.png) `d`"),
            [("texto", "a "), ("negrito", "b"), ("texto", " c "), ("link", "x|u"), ("texto", " "),
             ("imagem", "i|p.png"), ("texto", " "), ("codigo", "d")],
        )

    def test_inline_codigo_protege_marcacao(self):
        self.assertEqual(tokens_inline("`**x**`"), [("codigo", "**x**")])

    def test_citacao_com_link(self):
        c = [t for t in tokenizar(DOC) if t.tipo == "citacao"][0]
        self.assertIn(("link", "link|http://x.com"), c.inline)

    def test_vazio(self):
        self.assertEqual(tokenizar(""), [])
        self.assertEqual(tokenizar("\n\n  \n"), [])

    def test_cerca_til(self):
        t = tokenizar("~~~\nx\n~~~")
        self.assertEqual((t[0].tipo, t[0].texto), ("codigo", "x"))

    def test_codigo_sem_fechamento(self):
        with self.assertRaises(ErroMarkdown):
            tokenizar("```\nabc")


if __name__ == "__main__":
    unittest.main()
