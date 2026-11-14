"""Distância haversine, rumo inicial, ponto de destino e ponto médio na esfera."""
from __future__ import annotations

import math

RAIO_TERRA_KM = 6371.0088

Coord = tuple[float, float]  # (latitude, longitude) em graus


def _validar(c: Coord) -> None:
    if not -90 <= c[0] <= 90:
        raise ValueError(f"latitude fora de [-90, 90]: {c[0]}")
    if not -180 <= c[1] <= 180:
        raise ValueError(f"longitude fora de [-180, 180]: {c[1]}")


def distancia_km(a: Coord, b: Coord, raio: float = RAIO_TERRA_KM) -> float:
    _validar(a)
    _validar(b)
    f1, f2 = math.radians(a[0]), math.radians(b[0])
    df = f2 - f1
    dl = math.radians(b[1] - a[1])
    h = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * raio * math.asin(min(1.0, math.sqrt(h)))


def rumo_inicial(a: Coord, b: Coord) -> float:
    """Azimute inicial de a para b em graus [0, 360), 0 = norte."""
    _validar(a)
    _validar(b)
    f1, f2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(f2)
    x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def destino(a: Coord, rumo: float, distancia: float, raio: float = RAIO_TERRA_KM) -> Coord:
    """Ponto alcançado partindo de a com o rumo (graus) por `distancia` km."""
    _validar(a)
    f1, l1 = math.radians(a[0]), math.radians(a[1])
    br = math.radians(rumo)
    d = distancia / raio
    f2 = math.asin(math.sin(f1) * math.cos(d) + math.cos(f1) * math.sin(d) * math.cos(br))
    l2 = l1 + math.atan2(
        math.sin(br) * math.sin(d) * math.cos(f1), math.cos(d) - math.sin(f1) * math.sin(f2)
    )
    return (math.degrees(f2), (math.degrees(l2) + 540) % 360 - 180)


def ponto_medio(a: Coord, b: Coord) -> Coord:
    _validar(a)
    _validar(b)
    f1, f2 = math.radians(a[0]), math.radians(b[0])
    l1, dl = math.radians(a[1]), math.radians(b[1] - a[1])
    bx = math.cos(f2) * math.cos(dl)
    by = math.cos(f2) * math.sin(dl)
    fm = math.atan2(math.sin(f1) + math.sin(f2), math.hypot(math.cos(f1) + bx, by))
    lm = l1 + math.atan2(by, math.cos(f1) + bx)
    return (math.degrees(fm), (math.degrees(lm) + 540) % 360 - 180)
