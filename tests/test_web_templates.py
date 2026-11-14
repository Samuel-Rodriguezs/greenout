import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_templates import Ambiente, ErroTemplate


class Obj:
    nome = "Ana"
    _segredo = "x"

    def saudar(self):
        return "oi"


class TestWebTemplates(unittest.TestCase):
    def setUp(self):
        self.a = Ambiente()

    def r(self, fonte, **ctx):
        return self.a.renderizar_texto(fonte, **ctx)

    def test_variavel_e_escape(self):
        self.assertEqual(self.r("Olá {{ n }}!", n="<b>&\"'"), "Olá &lt;b&gt;&amp;&quot;&#x27;!")

    def test_safe_nao_escapa(self):
        self.assertEqual(self.r("{{ x|safe }}", x="<i>a</i>"), "<i>a</i>")

    def test_dotted_e_atributos(self):
        self.assertEqual(self.r("{{ u.nome }} {{ u.saudar }} {{ d.a.b }}",
                                u=Obj(), d={"a": {"b": 3}}), "Ana oi 3")
        self.assertEqual(self.r("[{{ faltando.x }}]"), "[]")

    def test_atributo_privado_bloqueado(self):
        with self.assertRaises(ErroTemplate):
            self.r("{{ u._segredo }}", u=Obj())

    def test_filtros(self):
        self.assertEqual(self.r("{{ x|upper }}-{{ l|length }}-{{ l|join:\"/\" }}", x="a", l=[1, 2]),
                         "A-2-1/2")
        self.assertEqual(self.r('{{ x|default:"vazio" }}'), "vazio")
        self.assertEqual(self.r('{{ x|default:"a|b" }}'), "a|b")
        with self.assertRaises(ErroTemplate):
            self.r("{{ x|inexistente }}")

    def test_if_else(self):
        t = "{% if a %}A{% else %}B{% endif %}"
        self.assertEqual(self.r(t, a=1), "A")
        self.assertEqual(self.r(t, a=0), "B")
        self.assertEqual(self.r("{% if not a and n > 2 %}ok{% endif %}", a=0, n=5), "ok")
        self.assertEqual(self.r('{% if s == "x" or n < 0 %}ok{% endif %}', s="x", n=1), "ok")

    def test_for_com_loop_e_vazio(self):
        t = "{% for i in xs %}{{ loop.indice }}:{{ i }}{% if not loop.ultimo %},{% endif %}{% else %}nada{% endfor %}"
        self.assertEqual(self.r(t, xs=["a", "b"]), "1:a,2:b")
        self.assertEqual(self.r(t, xs=[]), "nada")

    def test_comentario(self):
        self.assertEqual(self.r("a{# oculto #}b"), "ab")

    def test_heranca(self):
        a = Ambiente({
            "base": "<h1>{% block titulo %}Base{% endblock %}</h1><main>{% block corpo %}vazio{% endblock %}</main>",
            "meio": '{% extends "base" %}{% block titulo %}Meio {{ x }}{% endblock %}',
            "filho": '{% extends "meio" %}{% block corpo %}<{{ x }}>{% endblock %}',
        })
        self.assertEqual(a.renderizar("base"), "<h1>Base</h1><main>vazio</main>")
        self.assertEqual(a.renderizar("filho", x="&"),
                         "<h1>Meio &amp;</h1><main><&amp;></main>")

    def test_filho_sobrescreve_meio(self):
        a = Ambiente({
            "base": "[{% block a %}base{% endblock %}]",
            "meio": '{% extends "base" %}{% block a %}meio{% endblock %}',
            "filho": '{% extends "meio" %}{% block a %}filho{% endblock %}',
        })
        self.assertEqual(a.renderizar("filho"), "[filho]")

    def test_erros_estruturais(self):
        for fonte in ("{% if x %}", "{% for x %}a{% endfor %}", "{% block b %}", "{% foo %}",
                      '{% extends "x" %}{% extends "y" %}'):
            with self.assertRaises(ErroTemplate, msg=fonte):
                Ambiente({"t": fonte, "x": "", "y": ""}).renderizar("t")

    def test_nao_encontrado_e_circular(self):
        with self.assertRaises(ErroTemplate):
            self.a.renderizar("nada")
        a = Ambiente({"a": '{% extends "b" %}', "b": '{% extends "a" %}'})
        with self.assertRaises(ErroTemplate):
            a.renderizar("a")

    def test_adicionar_invalida_cache(self):
        a = Ambiente({"t": "um"})
        self.assertEqual(a.renderizar("t"), "um")
        a.adicionar("t", "dois")
        self.assertEqual(a.renderizar("t"), "dois")

    def test_none_vira_vazio(self):
        self.assertEqual(self.r("[{{ x }}]", x=None), "[]")


if __name__ == "__main__":
    unittest.main()
