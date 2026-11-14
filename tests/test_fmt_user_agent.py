import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_user_agent import parse

CHROME_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
EDGE = CHROME_WIN + " Edg/120.0.2210.91"
FIREFOX_LINUX = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
SAFARI_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
ANDROID = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


class TestFmtUserAgent(unittest.TestCase):
    def test_chrome_windows(self):
        ua = parse(CHROME_WIN)
        self.assertEqual((ua.navegador, ua.versao, ua.sistema, ua.dispositivo),
                         ("Chrome", "120.0.0.0", "Windows 10", "desktop"))

    def test_edge_antes_de_chrome(self):
        self.assertEqual(parse(EDGE).navegador, "Edge")

    def test_firefox_linux(self):
        ua = parse(FIREFOX_LINUX)
        self.assertEqual((ua.navegador, ua.sistema), ("Firefox", "Linux"))

    def test_safari_mac(self):
        ua = parse(SAFARI_MAC)
        self.assertEqual((ua.navegador, ua.versao, ua.sistema), ("Safari", "17.1", "macOS 10.15.7"))

    def test_mobile(self):
        ip = parse(IPHONE)
        self.assertEqual((ip.sistema, ip.dispositivo), ("iOS 17.1", "mobile"))
        an = parse(ANDROID)
        self.assertEqual((an.navegador, an.sistema, an.dispositivo), ("Chrome", "Android 13", "mobile"))

    def test_tablet(self):
        self.assertEqual(parse("Mozilla/5.0 (Linux; Android 12; SM-T500) Chrome/110.0 Safari/537.36").dispositivo, "tablet")

    def test_bot(self):
        ua = parse(GOOGLEBOT)
        self.assertTrue(ua.bot)
        self.assertEqual((ua.navegador, ua.versao, ua.dispositivo), ("Googlebot", "2.1", "bot"))

    def test_curl_e_desconhecido(self):
        self.assertEqual(parse("curl/8.4.0").navegador, "curl")
        ua = parse("")
        self.assertEqual((ua.navegador, ua.sistema, ua.dispositivo), ("Desconhecido", "Desconhecido", "desktop"))
        self.assertEqual(parse("###???").navegador, "Desconhecido")


if __name__ == "__main__":
    unittest.main()
