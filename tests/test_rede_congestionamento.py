import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_congestionamento import Congestionamento, simular, vazao_media


class TestRedeCongestionamento(unittest.TestCase):
    def test_slow_start_e_aimd(self):
        self.assertEqual(simular(8, ssthresh=8), [1, 2, 4, 8, 9, 10, 11, 12])

    def test_timeout_reinicia(self):
        # no RTT 6 cwnd=11 -> ssthresh=5.5, cwnd=1
        t = simular(11, {6: "timeout"}, ssthresh=8)
        self.assertEqual(t[6], 11)
        self.assertEqual(t[7:], [1, 2, 4, 5.5])

    def test_dupack_reno_vs_tahoe(self):
        reno = simular(8, {5: "dupack"}, "reno", 8)
        tahoe = simular(8, {5: "dupack"}, "tahoe", 8)
        self.assertEqual(reno[5], 10)
        self.assertEqual(reno[6:], [5, 6])  # cwnd = ssthresh = 5, depois +1
        self.assertEqual(tahoe[6:], [1, 2])

    def test_ssthresh_minimo(self):
        c = Congestionamento(cwnd=2, ssthresh=4)
        c.perda("timeout")
        self.assertEqual((c.cwnd, c.ssthresh), (1.0, 2.0))

    def test_fase(self):
        c = Congestionamento(ssthresh=4)
        self.assertEqual(c.fase, "slow_start")
        c.rtt_sem_perda()
        c.rtt_sem_perda()
        self.assertEqual(c.cwnd, 4)
        self.assertEqual(c.fase, "congestion_avoidance")
        c.perda("timeout")
        self.assertEqual(c.fase, "slow_start")

    def test_serrote(self):
        t = simular(40, {r: "dupack" for r in (15, 25, 35)}, "reno", 16)
        self.assertEqual(t[15], 27)  # 16 no RTT 4, +1 por RTT até o RTT 15
        self.assertEqual(t[16], 13.5)  # metade após o dupack
        self.assertEqual(t[25], 22.5)
        self.assertEqual(max(t), 27)

    def test_vazao(self):
        self.assertAlmostEqual(vazao_media([1, 2, 3], 1000, 0.1), 20000.0)
        with self.assertRaises(ValueError):
            vazao_media([], 1000, 0.1)
        with self.assertRaises(ValueError):
            vazao_media([1], 1000, 0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Congestionamento(variante="cubic")
        with self.assertRaises(ValueError):
            Congestionamento().perda("x")


if __name__ == "__main__":
    unittest.main()
