import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_fusos import com_fuso, converter, formatar_offset, offset_em_minutos, para_tzinfo


class TestFusos(unittest.TestCase):
    def test_offsets(self) -> None:
        self.assertEqual(offset_em_minutos("BRT"), -180)
        self.assertEqual(offset_em_minutos("brt"), -180)
        self.assertEqual(offset_em_minutos("UTC"), 0)
        self.assertEqual(offset_em_minutos("+05:30"), 330)
        self.assertEqual(offset_em_minutos("UTC-3"), -180)
        self.assertEqual(offset_em_minutos("-0300"), -180)
        self.assertEqual(offset_em_minutos("GMT+14"), 840)

    def test_invalidos(self) -> None:
        for f in ("XYZ", "", "+15:00", "+05:60", "UTC+"):
            with self.subTest(f=f):
                with self.assertRaises(ValueError):
                    offset_em_minutos(f)

    def test_converter_brt_para_utc(self) -> None:
        self.assertEqual(
            converter(datetime(2026, 11, 14, 22, 0), "BRT", "UTC"), datetime(2026, 11, 15, 1, 0)
        )

    def test_converter_com_virada_de_ano_e_meia_hora(self) -> None:
        self.assertEqual(
            converter(datetime(2026, 12, 31, 20, 0), "BRT", "IST"), datetime(2027, 1, 1, 4, 30)
        )

    def test_ida_e_volta(self) -> None:
        original = datetime(2026, 3, 1, 12, 15)
        for destino in ("JST", "PST", "+05:45", "-03:30"):
            with self.subTest(destino=destino):
                ida = converter(original, "BRT", destino)
                self.assertEqual(converter(ida, destino, "BRT"), original)

    def test_mesmo_fuso(self) -> None:
        d = datetime(2026, 1, 1, 0, 0)
        self.assertEqual(converter(d, "BRT", "-03:00"), d)

    def test_com_fuso_coerente_com_stdlib(self) -> None:
        d = com_fuso(datetime(2026, 11, 14, 22, 0), "BRT")
        self.assertEqual(d.astimezone(timezone.utc).replace(tzinfo=None), datetime(2026, 11, 15, 1, 0))
        self.assertEqual(para_tzinfo("IST").utcoffset(None), timedelta(hours=5, minutes=30))

    def test_rejeita_datetime_com_fuso(self) -> None:
        aware = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            converter(aware, "UTC", "BRT")
        with self.assertRaises(ValueError):
            com_fuso(aware, "BRT")

    def test_formatar_offset(self) -> None:
        self.assertEqual(formatar_offset("BRT"), "-03:00")
        self.assertEqual(formatar_offset("IST"), "+05:30")
        self.assertEqual(formatar_offset("UTC"), "+00:00")


if __name__ == "__main__":
    unittest.main()
