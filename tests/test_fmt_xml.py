import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_xml import ErroXml, No, parse, serializar


class TestFmtXml(unittest.TestCase):
    def test_arvore(self):
        r = parse('<?xml version="1.0"?><a x="1" y=\'2\'><b>oi</b><c/><b>tchau</b></a>')
        self.assertEqual(r.tag, "a")
        self.assertEqual(r.atributos, {"x": "1", "y": "2"})
        self.assertEqual([f.tag for f in r.filhos], ["b", "c", "b"])
        self.assertEqual([b.texto for b in r.buscar("b")], ["oi", "tchau"])

    def test_entidades_cdata_comentario(self):
        r = parse('<a t="&lt;&amp;">x &gt; y &#65;<!-- c --><![CDATA[<raw>]]></a>')
        self.assertEqual(r.atributos["t"], "<&")
        self.assertEqual(r.texto, "x > y A<raw>")

    def test_doctype_e_espacos(self):
        r = parse("<!DOCTYPE a>\n<a>\n  <b/>\n</a>\n")
        self.assertEqual(len(r.filhos), 1)
        self.assertEqual(r.texto_total().strip(), "")

    def test_ida_e_volta(self):
        xml = '<a k="v&quot;"><b>1 &lt; 2</b><c/></a>'
        self.assertEqual(serializar(parse(xml)), xml)
        self.assertEqual(serializar(No("x", {"a": "b"})), '<x a="b"/>')

    def test_malformados(self):
        for ruim in ["<a><b></a></b>", "<a>", "</a>", "<a/><b/>", "texto", "", "<a x=1/>",
                     "<a x='1' x='2'/>", "<a>&foo;</a>", "<a><!-- x</a>", "<a>oi</a>lixo", "<1a/>",
                     "<a><![CDATA[x</a>"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroXml):
                    parse(ruim)


if __name__ == "__main__":
    unittest.main()
