#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera docs/pcb/layout-pcb-borrador.pdf (trazado de pistas de la PCB casera, borrador).

Requisitos: python3, cairosvg (pip install cairosvg) y pdfunite (poppler-utils).
Uso:        python3 docs/pcb/generar_layout.py

El trazado se define a mano sobre una rejilla de 2,54 mm (unidades "u"). Las redes esperadas salen
de CONEXIONES en generar_esquematico.py. verificar() calcula la conectividad por geometria
(pistas y pads que se tocan) y la compara con esa lista, y comprueba anchos y separaciones.
Dimensiones PROVISIONALES (cambiar aqui y regenerar): FILA_MM, PASO_BORNE_MM.
"""
import html
import math
import os
import subprocess
import sys
import tempfile
import textwrap
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True        # no dejar __pycache__ en docs/pcb
sys.path.insert(0, AQUI)
import cairosvg                                   # noqa: E402
import generar_esquematico as esq                 # noqa: E402

SALIDA = os.path.join(AQUI, 'layout-pcb-borrador.pdf')
FECHA = '2026-11-12'
FUENTE = 'Arial, Helvetica, sans-serif'

# ---------------------------------------------------------------- parametros
U = 2.54                      # rejilla (mm)
FILA_MM = 25.4                # PROVISIONAL: distancia entre las dos filas de pines del NodeMCU-32S
PASO_BORNE_MM = 5.08          # PROVISIONAL: paso del borne de tornillo (5,0 o 5,08 mm)
W_SENAL = 0.8                 # mm, pistas de senal
W_POT = 2.0                   # mm, pistas de potencia
MIN_SENAL, MIN_POT, SEPARACION, MARGEN = 0.5, 2.0, 0.5, 2.0   # reglas de la hoja 4 del esquematico
BORDE = (1.0 * U, 35.5 * U, 1.5 * U, 41.5 * U)                # x0, x1, y0, y1 de la placa (mm)

# ---------------------------------------------------------------- geometria de la placa
PADS = {}
TRACKS = []
yB = 3.0
yA = yB + FILA_MM / U


def pad(ref, pin, x, y, d=2.0, drill=1.0):
    PADS[(ref, pin)] = dict(ref=ref, pin=pin, x=x * U, y=y * U, d=d, drill=drill)


def pp(ref, pin):
    p = PADS[(ref, pin)]
    return (p['x'] / U, p['y'] / U)


def trk(nombre, pts, ancho, clase):
    TRACKS.append(dict(nombre=nombre, pts=[(a * U, b * U) for a, b in pts], w=ancho, cls=clase))


# zocalos del ESP32: USB a la derecha (supuesto), fila B al norte, fila A al sur, pin 1 al oeste
for k in range(1, 20):
    pad('U1', f'A{k}', 6 + k - 1, yA)
    pad('U1', f'B{k}', 6 + k - 1, yB)
# sensores (tiras de pines)
pad('J1', '1', 6, 17); pad('J1', '2', 5, 17); pad('J1', '3', 4, 17)
pad('J2', '1', 12, 17); pad('J2', '2', 11, 17); pad('J2', '3', 10, 17)
pad('J3', '1', 16, 17); pad('J3', '2', 17, 17)
# etapa del cooler (oeste)
pad('R3', '1', 3, 27); pad('R3', '2', 6, 27)
pad('R4', '1', 6, 25); pad('R4', '2', 6, 22)
pad('Q2', 'G', 7, 27); pad('Q2', 'D', 8, 27); pad('Q2', 'S', 9, 27)
pad('D2', 'A', 8, 30); pad('D2', 'K', 8, 34)
pad('J6', '2', 11, 32, 3.0, 1.3); pad('J6', '1', 11, 34, 3.0, 1.3)
# etapa de la bomba (centro)
pad('R1', '1', 15, 27); pad('R1', '2', 18, 27)
pad('R2', '1', 18, 25); pad('R2', '2', 18, 22)
pad('Q1', 'G', 19, 27); pad('Q1', 'D', 20, 27); pad('Q1', 'S', 21, 27)
pad('D1', 'A', 20, 30); pad('D1', 'K', 20, 34)
pad('J5', '2', 23, 32, 3.0, 1.3); pad('J5', '1', 23, 34, 3.0, 1.3)
# entrada de 12 V
pad('F1', '2', 27, 34, 3.0, 1.3); pad('F1', '1', 29, 34, 3.0, 1.3)
pad('J4', '1', 31, 34, 3.0, 1.3); pad('J4', '2', 31, 36, 3.0, 1.3)
pad('C1', '+', 25, 38, 2.4, 1.0); pad('C1', '-', 25, 40, 2.4, 1.0)
# puente de cable (cruza la pista de GPIO26)
pad('W1', '1', 14, 22, 2.4, 0.8); pad('W1', '2', 16, 22, 2.4, 0.8)

# pistas de senal (0,8 mm)
trk('GPIO17', [pp('U1', 'B11'), (16, 4), (3, 4), pp('R3', '1')], W_SENAL, 'senal')
trk('GPIO4', [pp('U1', 'B13'), (18, 5), (5, 5), pp('J1', '2')], W_SENAL, 'senal')
trk('GPIO34', [pp('U1', 'A5'), pp('J2', '3')], W_SENAL, 'senal')
trk('GPIO27', [pp('U1', 'A11'), pp('J3', '1')], W_SENAL, 'senal')
trk('GPIO26', [pp('U1', 'A10'), pp('R1', '1')], W_SENAL, 'senal')
trk('+3V3', [pp('U1', 'A1'), (6, 19), (11, 19), pp('J2', '2')], W_SENAL, 'senal')
trk('GND J1', [pp('J1', '3'), (4, 22)], W_SENAL, 'senal')
trk('GND J2', [pp('J2', '1'), (12, 22)], W_SENAL, 'senal')
trk('GND A14', [pp('U1', 'A14'), (19, 22)], W_SENAL, 'senal')
trk('GND J3', [pp('J3', '2'), (19, 17)], W_SENAL, 'senal')
trk('GATE cooler 1', [pp('R3', '2'), pp('Q2', 'G')], W_SENAL, 'senal')
trk('GATE cooler 2', [pp('R3', '2'), pp('R4', '1')], W_SENAL, 'senal')
trk('GATE bomba 1', [pp('R1', '2'), pp('Q1', 'G')], W_SENAL, 'senal')
trk('GATE bomba 2', [pp('R1', '2'), pp('R2', '1')], W_SENAL, 'senal')
# pistas de potencia (2,0 mm)
trk('GND oeste', [(4, 22), pp('W1', '1')], W_POT, 'potencia')
trk('GND este', [pp('W1', '2'), (34, 22)], W_POT, 'potencia')
trk('S cooler', [pp('Q2', 'S'), (9, 22)], W_POT, 'potencia')
trk('S bomba', [pp('Q1', 'S'), (21, 22)], W_POT, 'potencia')
trk('GND anillo', [(34, 22), (34, 40), pp('C1', '-')], W_POT, 'potencia')
trk('GND J4', [pp('J4', '2'), (31, 40)], W_POT, 'potencia')
trk('+12V troncal', [pp('D2', 'K'), pp('F1', '2')], W_POT, 'potencia')
trk('+12V C1', [(25, 34), pp('C1', '+')], W_POT, 'potencia')
trk('12V_IN', [pp('F1', '1'), pp('J4', '1')], W_POT, 'potencia')
trk('Drenador cooler 1', [pp('Q2', 'D'), pp('D2', 'A')], W_POT, 'potencia')
trk('Drenador cooler 2', [pp('J6', '2'), (11, 30), (8, 30)], W_POT, 'potencia')
trk('Drenador bomba 1', [pp('Q1', 'D'), pp('D1', 'A')], W_POT, 'potencia')
trk('Drenador bomba 2', [pp('J5', '2'), (23, 30), (20, 30)], W_POT, 'potencia')


# ---------------------------------------------------------------- verificacion
def red_esperada(clave):
    if clave in esq.NET:
        return esq.NET[clave]
    if clave[0] == 'W1':
        return 'GND'
    return f'NC:{clave[0]}.{clave[1]}'


def formas():
    S = []
    for k, p in PADS.items():
        S.append(dict(kind='c', cx=p['x'], cy=p['y'], r=p['d'] / 2, owner=('pad', k)))
    for i, t in enumerate(TRACKS):
        h = t['w'] / 2
        for (x0, y0), (x1, y1) in zip(t['pts'], t['pts'][1:]):
            assert math.isclose(x0, x1, abs_tol=1e-9) or math.isclose(y0, y1, abs_tol=1e-9), t['nombre']
            S.append(dict(kind='r', x0=min(x0, x1) - h, x1=max(x0, x1) + h,
                          y0=min(y0, y1) - h, y1=max(y0, y1) + h, owner=('trk', i)))
    return S


def distancia(a, b):
    if a['kind'] == 'c' and b['kind'] == 'c':
        return max(0.0, math.hypot(a['cx'] - b['cx'], a['cy'] - b['cy']) - a['r'] - b['r'])
    if a['kind'] == 'r' and b['kind'] == 'r':
        dx = max(0.0, a['x0'] - b['x1'], b['x0'] - a['x1'])
        dy = max(0.0, a['y0'] - b['y1'], b['y0'] - a['y1'])
        return math.hypot(dx, dy)
    c, r = (a, b) if a['kind'] == 'c' else (b, a)
    dx = max(0.0, r['x0'] - c['cx'], c['cx'] - r['x1'])
    dy = max(0.0, r['y0'] - c['cy'], c['cy'] - r['y1'])
    return max(0.0, math.hypot(dx, dy) - c['r'])


def verificar():
    res = []
    fallos = []

    def check(cond, msg):
        res.append((bool(cond), msg))
        print('OK   ' if cond else 'FALLO', msg)
        if not cond:
            fallos.append(msg)

    S = formas()
    padre = list(range(len(S)))

    def find(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            if distancia(S[i], S[j]) <= 1e-6:
                padre[find(i)] = find(j)
    comp = defaultdict(list)
    for i in range(len(S)):
        comp[find(i)].append(i)

    check(all(k in PADS for k in esq.NET), 'todos los pines del esquemático tienen pad en la placa')
    redes_comp, cortos, flotantes = {}, [], []
    for c, idx in comp.items():
        redes = {red_esperada(S[i]['owner'][1]) for i in idx if S[i]['owner'][0] == 'pad'}
        if not redes:
            flotantes.append(idx)
        elif len(redes) > 1:
            cortos.append(redes)
        else:
            redes_comp[c] = redes.pop()
    check(not flotantes, 'no hay cobre suelto sin pad')
    check(not cortos, 'no hay cortos entre redes distintas' + (f' (cortos: {cortos})' if cortos else ''))

    # redes completas, contando el puente de cable W1 como union de sus dos pads
    pad_comp = {}
    for c, idx in comp.items():
        for i in idx:
            if S[i]['owner'][0] == 'pad':
                pad_comp[S[i]['owner'][1]] = c
    union = {c: c for c in comp}

    def fu(c):
        while union[c] != c:
            c = union[c]
        return c
    union[fu(pad_comp[('W1', '1')])] = fu(pad_comp[('W1', '2')])
    abiertas = []
    por_red = defaultdict(set)
    for (ref, pin), n in esq.NET.items():
        por_red[n].add(fu(pad_comp[(ref, pin)]))
    for n, cs in por_red.items():
        if len(cs) != 1:
            abiertas.append(n)
    check(not abiertas, 'cada red del esquemático queda unida (con el puente W1)' + (f' (abiertas: {abiertas})' if abiertas else ''))
    sin_puente = defaultdict(set)
    for (ref, pin), n in esq.NET.items():
        sin_puente[n].add(pad_comp[(ref, pin)])
    sin_p = sorted(n for n, cs in sin_puente.items() if len(cs) > 1)
    check(sin_p == ['GND'], f'solo GND necesita el puente de cable (redes partidas sin W1: {sin_p})')
    nc = [k for k in PADS if red_esperada(k).startswith('NC:')]
    aisl = all(len(comp[find(next(i for i, s in enumerate(S) if s['owner'] == ('pad', k)))]) == 1 for k in nc)
    check(aisl, f'los {len(nc)} pads sin uso del zócalo quedan aislados')

    # anchos y separaciones
    check(all(t['w'] >= (MIN_POT if t['cls'] == 'potencia' else MIN_SENAL) - 1e-9 for t in TRACKS),
          f'anchos: potencia >= {MIN_POT} mm, señal >= {MIN_SENAL} mm')
    minimo = (9e9, None)
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            ci, cj = find(i), find(j)
            if ci == cj or redes_comp.get(ci) == redes_comp.get(cj):
                continue
            d = distancia(S[i], S[j])
            if d < minimo[0]:
                minimo = (d, (S[i]['owner'], S[j]['owner']))
    check(minimo[0] >= SEPARACION - 1e-6, f'separación mínima entre redes distintas: {minimo[0]:.2f} mm (mínimo {SEPARACION} mm)')
    x0, x1, y0, y1 = BORDE
    margen = min(min(s['cx'] - s['r'] - x0, x1 - s['cx'] - s['r'], s['cy'] - s['r'] - y0, y1 - s['cy'] - s['r'])
                 if s['kind'] == 'c' else
                 min(s['x0'] - x0, x1 - s['x1'], s['y0'] - y0, y1 - s['y1']) for s in S)
    check(margen >= MARGEN, f'margen del cobre al borde de la placa: {margen:.2f} mm (mínimo {MARGEN} mm)')
    check(all((p['d'] - p['drill']) / 2 >= 0.45 for p in PADS.values()), 'anillo de cobre de cada pad >= 0,45 mm')

    # el puente W1 cruza solo la pista de GPIO26
    a, b = PADS[('W1', '1')], PADS[('W1', '2')]
    cruza = set()
    for i, s in enumerate(S):
        if s['owner'][0] != 'trk' or not (s['y0'] < a['y'] < s['y1']):
            continue
        cx = (s['x0'] + s['x1']) / 2
        if min(a['x'], b['x']) + 1e-6 < cx < max(a['x'], b['x']) - 1e-6:      # pasa entre los dos pads
            cruza.add(TRACKS[s['owner'][1]]['nombre'])
    check(cruza == {'GPIO26'}, f'el puente W1 ({math.hypot(a["x"] - b["x"], a["y"] - b["y"]):.2f} mm) cruza solo la pista GPIO26: {sorted(cruza)}')
    return res, fallos


# ---------------------------------------------------------------- dibujo (mm)
class Pag:
    def __init__(self):
        self.e = []

    def add(self, s):
        self.e.append(s)

    def text(self, x, y, t, size=3.0, fill='#111', anchor='start', weight='normal', rot=None):
        tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" font-family="{FUENTE}"{tr}>{html.escape(t, quote=False)}</text>')

    def line(self, x1, y1, x2, y2, color='#111', w=0.3, dash=None, cap='butt'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d}/>')

    def rect(self, x, y, w, h, fill='none', stroke='#111', sw=0.3, dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circ(self, x, y, r, fill='#111', stroke='none', sw=0.2):
        self.add(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def poli(self, pts, color, w, opacity=1.0):
        p = ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)
        self.add(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="square" '
                 f'stroke-linejoin="miter" opacity="{opacity}"/>')

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
                '<rect width="210" height="297" fill="#ffffff"/>' + ''.join(self.e) + '</svg>')


def p(ref, pin):
    q = PADS[(ref, pin)]
    return q['x'], q['y']


def cobre(g, color, mirror_hole='#ffffff', opacidad=1.0):
    for t in TRACKS:
        g.poli(t['pts'], color, t['w'], opacidad)
    for q in PADS.values():
        g.circ(q['x'], q['y'], q['d'] / 2, color)
        g.circ(q['x'], q['y'], 0.3, mirror_hole)


def resistencia(g, ref, valor, a, b):
    (x0, y0), (x1, y1) = p(*a), p(*b)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    g.line(x0, y0, x1, y1, '#333', 0.4)
    if abs(y0 - y1) < 1e-6:
        g.rect(xm - 3.15, ym - 1.2, 6.3, 2.4, '#e9d8a6', '#333', 0.25)
        g.text(xm, ym - 2.0, ref, 2.4, '#111', 'middle', 'bold')
    else:
        g.rect(xm - 1.2, ym - 3.15, 2.4, 6.3, '#e9d8a6', '#333', 0.25)
        g.text(xm + 2.0, ym + 0.8, ref, 2.4, '#111', 'start', 'bold')


def diodo(g, ref, anodo, catodo):
    (xa, ya), (xk, yk) = p(*anodo), p(*catodo)
    xm, ym = (xa + xk) / 2, (ya + yk) / 2
    g.line(xa, ya, xk, yk, '#333', 0.4)
    g.rect(xm - 1.35, ym - 2.6, 2.7, 5.2, '#2b2b2b', '#111', 0.25)
    ykb = ym - 2.6 if yk < ya else ym + 1.6
    g.rect(xm - 1.35, ykb, 2.7, 1.0, '#e5e7eb', '#111', 0.2)
    g.text(xm - 2.0, ym + 0.8, ref, 2.4, '#111', 'end', 'bold')


def mosfet(g, ref, gp, dp, sp):
    (xd, yd) = p(*dp)
    g.rect(xd - 5.1, yd + 1.3, 10.2, 4.6, '#d1d5db', '#111', 0.3)
    g.rect(xd - 5.1, yd + 5.1, 10.2, 0.8, '#6b7280', '#111', 0.2)
    g.text(xd, yd + 4.2, ref, 2.6, '#111', 'middle', 'bold')
    for (r, pin), t in ((gp, 'G'), (dp, 'D'), (sp, 'S')):
        x, y = p(r, pin)
        g.text(x, y - 1.6, t, 2.4, '#111', 'middle', 'bold')


def borne(g, ref, titulo, a, b, notas):
    (x0, y0), (x1, y1) = p(*a), p(*b)
    xm = (x0 + x1) / 2
    g.rect(xm - 3.8, min(y0, y1) - 2.8, 7.6, abs(y1 - y0) + 5.6, '#bbf7d0', '#14532d', 0.3)
    g.text(xm, min(y0, y1) - 3.4, ref, 2.6, '#111', 'middle', 'bold')


def cabecera(g, titulo, n, total=3):
    g.text(15, 15, titulo, 6.0, '#111', 'start', 'bold')
    g.text(15, 22, 'BORRADOR sobre el papel: sin construir ni probar. Las dimensiones marcadas PROVISIONAL deben medirse.',
           3.0, '#b00020')
    g.text(195, 290, f'Hoja {n} de {total} · {FECHA}', 2.8, '#555', 'end')


def hoja_componentes():
    g = Pag()
    cabecera(g, 'Trazado (borrador) · vista de componentes, escala 1:1', 1)
    x0, x1, y0, y1 = BORDE
    ox, oy = 15 - x0, 35 - y0
    g.add(f'<g transform="translate({ox:.3f},{oy:.3f})">')
    g.rect(x0, y0, x1 - x0, y1 - y0, '#f5f3ea', '#555', 0.3)
    ux = 1
    while ux * U < x1:
        uy = 1
        while uy * U < y1:
            if x0 < ux * U < x1 and y0 < uy * U < y1:
                g.circ(ux * U, uy * U, 0.12, '#d6d2c2')
            uy += 1
        ux += 1
    cobre(g, '#c77d00', '#f5f3ea', 0.55)
    # modulo ESP32 (supuesto: USB a la derecha)
    ax, bx = 6 * U, 24 * U
    g.rect(ax - 4.64, yB * U - 1.3, bx - ax + 9.28, (yA - yB) * U + 2.6, 'none', '#1d4ed8', 0.35, '2 1.2')
    g.rect(bx + 4.64, (yB + yA) / 2 * U - 3.5, 2.2, 7.0, '#c0c0c0', '#555', 0.25)
    g.text((ax + bx) / 2, (yB + yA) / 2 * U - 1.0, 'ESP32 NodeMCU-32S (zócalos U1)', 3.2, '#1d4ed8', 'middle', 'bold')
    g.text((ax + bx) / 2, (yB + yA) / 2 * U + 3.2, 'vista superior · USB → derecha · fila B arriba, fila A abajo', 2.6, '#1d4ed8', 'middle')
    g.text(bx + 8.6, (yB + yA) / 2 * U + 1.0, 'USB', 2.6, '#555')
    for fila, y in (('A', yA), ('B', yB)):
        g.rect(ax - 1.27, y * U - 1.27, bx - ax + 2.54, 2.54, 'none', '#111', 0.3)
    for fila, k, y, off in (('B', 1, yB, -2.4), ('B', 19, yB, -2.4), ('A', 19, yA, 3.5)):
        g.text((6 + k - 1) * U, y * U + off, f'{fila}{k}', 2.2, '#555', 'middle')
    for (ref, pin), n in esq.NET.items():
        if ref == 'U1':
            x, y = p(ref, pin)
            fila = pin[0]
            desplaza = {'A10': 3.4, 'A11': 6.4}.get(pin, 3.4)
            g.text(x, y + (desplaza if fila == 'A' else -2.4), esq.U1_ROTULO[pin], 2.2, '#111', 'middle', 'bold')
    # conectores de sensores
    for ref, titulo, pines in (('J1', 'J1 DHT11', ['+3V3', 'DATA', 'GND']),
                               ('J2', 'J2 Suelo', ['GND', 'VCC', 'AOUT']),
                               ('J3', 'J3 Flotador', ['hilo 1', 'hilo 2'])):
        xs = [p(ref, str(i + 1))[0] for i in range(len(pines))]
        y = p(ref, '1')[1]
        g.rect(min(xs) - 1.27, y - 1.27, max(xs) - min(xs) + 2.54, 2.54, 'none', '#111', 0.3)
        for i, t in enumerate(pines):
            g.text(xs[i], y + 4.0, f'{i + 1}', 2.2, '#555', 'middle')
        g.text((min(xs) + max(xs)) / 2, y + 7.2, ref, 2.6, '#111', 'middle', 'bold')
    # etapa de potencia
    resistencia(g, 'R1', '220Ω', ('R1', '1'), ('R1', '2'))
    resistencia(g, 'R2', '10kΩ', ('R2', '1'), ('R2', '2'))
    resistencia(g, 'R3', '220Ω', ('R3', '1'), ('R3', '2'))
    resistencia(g, 'R4', '10kΩ', ('R4', '1'), ('R4', '2'))
    diodo(g, 'D1', ('D1', 'A'), ('D1', 'K'))
    diodo(g, 'D2', ('D2', 'A'), ('D2', 'K'))
    mosfet(g, 'Q1', ('Q1', 'G'), ('Q1', 'D'), ('Q1', 'S'))
    mosfet(g, 'Q2', ('Q2', 'G'), ('Q2', 'D'), ('Q2', 'S'))
    borne(g, 'J5', 'Bomba', ('J5', '2'), ('J5', '1'), ['1 = +12 V', '2 = drenador'])
    borne(g, 'J6', 'Cooler', ('J6', '2'), ('J6', '1'), ['1 = +12 V', '2 = drenador'])
    borne(g, 'J4', 'Fuente 12 V', ('J4', '1'), ('J4', '2'), ['1 = +12 V', '2 = GND'])
    for a, b, t in (('F1', '2', None),):
        (xf1, yf1), (xf2, yf2) = p('F1', '2'), p('F1', '1')
        g.rect(xf1 - 2.0, yf1 - 2.4, xf2 - xf1 + 4.0, 4.8, 'none', '#111', 0.3, '1.2 0.8')
        g.text((xf1 + xf2) / 2, yf1 - 3.4, 'F1', 2.6, '#111', 'middle', 'bold')
    xc, yc = p('C1', '+')[0], (p('C1', '+')[1] + p('C1', '-')[1]) / 2
    g.circ(xc, yc, 6.25, 'none', '#111', 0.3)
    g.text(xc + 7.4, yc - 0.4, 'C1', 2.6, '#111', 'start', 'bold')
    g.text(xc + 7.4, yc + 2.6, '+ arriba', 2.2, '#555')
    xw1, yw1 = p('W1', '1')
    xw2, yw2 = p('W1', '2')
    g.line(xw1, yw1, xw2, yw2, '#111', 0.9, cap='round')
    g.text((xw1 + xw2) / 2, yw1 + 4.4, 'W1', 2.6, '#111', 'middle', 'bold')
    # rotulos de potencia
    g.text(p('J4', '1')[0], p('J4', '1')[1] - 5.2, '+12V', 2.4, '#9d0208', 'middle', 'bold')
    g.text(p('J4', '2')[0] + 4.6, p('J4', '2')[1] + 0.8, 'GND', 2.4, '#222', 'start', 'bold')
    g.text(x0 + 1.0, 22 * U - 2.0, 'GND', 2.4, '#222', 'start', 'bold')
    g.add('</g>')
    # medidas
    ancho, alto = x1 - x0, y1 - y0
    g.text(15 + ancho / 2, 35 + alto + 5, f'placa {ancho:.1f} × {alto:.1f} mm', 3.0, '#111', 'middle', 'bold')
    # leyenda
    lx, ly = 112, 38
    g.text(lx, ly, 'Leyenda', 4.0, '#111', 'start', 'bold')
    g.rect(lx, ly + 3, 4, 2.4, '#d4a017', '#9a6a00', 0.2)
    g.text(lx + 6, ly + 5, 'pad (hay un agujero en cada uno)', 2.8)
    g.line(lx, ly + 10, lx + 4, ly + 10, '#c77d00', 0.8)
    g.text(lx + 6, ly + 11, 'pista de cobre (cara inferior, vista por transparencia)', 2.8)
    g.line(lx, ly + 16, lx + 4, ly + 16, '#1d4ed8', 0.4, '1 0.6')
    g.text(lx + 6, ly + 17, 'contorno del módulo ESP32', 2.8)
    g.text(lx, ly + 26, 'Para comprobar antes de grabar', 3.4, '#b00020', 'start', 'bold')
    notas = [
        'Imprime esta hoja al 100 % (sin ajustar a la página) y coloca encima el NodeMCU-32S y las piezas.',
        'Orientación del ESP32 (SUPUESTO): con la placa vista desde arriba y el USB a la derecha, la fila A (3V3 … 5V) va abajo y la fila B (GND … CLK) arriba, con el pin 1 a la izquierda. Verifícalo con tu placa.',
        f'Distancia entre filas de pines: {FILA_MM:.1f} mm, PROVISIONAL. Mide la tuya, cámbiala en el script y regenera.',
        f'Paso de los bornes de tornillo: {PASO_BORNE_MM:.2f} mm, PROVISIONAL (el dibujo usa 2 cuadros = 5,08 mm).',
        'Las pistas de potencia son de 2 mm; las de señal, de 0,8 mm.',
        'W1 es un alambre AISLADO que pasa por encima de la pista de P26; sin aislante la pista de P26 se pondría a GND.',
        'Falta un portafusible con cables (formato por definir) para F1.',
    ]
    y = ly + 31
    refs_tabla = [('U1', 'Zócalos del NodeMCU-32S (2 × 19)'), ('J1', 'DHT11 (+3V3, datos, GND)'), ('J2', 'Suelo (GND, VCC, AOUT)'),
                  ('J3', 'Flotador (2 hilos)'), ('J4', 'Fuente 12 V (1 +12 V, 2 GND)'), ('J5', 'Bomba (1 +12 V, 2 drenador)'),
                  ('J6', 'Cooler (1 +12 V, 2 drenador)'), ('F1', 'Fusible 3 A (portafusible con cables)'),
                  ('C1', '1000 µF / 25 V, + arriba'), ('Q1, Q2', 'IRLZ44N: G, D, S (de frente)'),
                  ('R1, R3', '220 Ω'), ('R2, R4', '10 kΩ'), ('D1, D2', '1N5819, banda = cátodo (+12 V)'),
                  ('W1', 'puente de cable aislado')]
    for n in notas:
        for k, linea in enumerate(textwrap.wrap(n, 52)):
            g.text(lx + (0 if k == 0 else 3), y, ('• ' if k == 0 else '') + linea, 2.8)
            y += 3.7
        y += 1.2
    y += 6
    g.text(lx, y, 'Referencias', 3.4, '#111', 'start', 'bold')
    for k, (a, b) in enumerate(refs_tabla):
        g.text(lx, y + 6 + k * 3.8, a, 2.8, '#111', 'start', 'bold')
        g.text(lx + 17, y + 6 + k * 3.8, b, 2.8)
    return g


def hoja_cobre():
    g = Pag()
    cabecera(g, 'Trazado (borrador) · cobre en espejo para imprimir', 2)
    x0, x1, y0, y1 = BORDE
    ancho = x1 - x0
    ox, oy = 15, 35
    g.add(f'<g transform="translate({ox + ancho:.3f},{oy:.3f}) scale(-1,1) translate({-x0:.3f},{-y0:.3f})">')
    g.rect(x0, y0, x1 - x0, y1 - y0, 'none', '#777', 0.15, '2 2')
    cobre(g, '#000000', '#ffffff', 1.0)
    g.add('</g>')
    sy = oy + (y1 - y0) + 10
    g.line(15, sy, 65, sy, '#000', 0.4)
    for k in range(6):
        g.line(15 + k * 10, sy - 1.5, 15 + k * 10, sy + 1.5, '#000', 0.4)
    g.text(15, sy + 6, 'Barra de escala: debe medir 50 mm en el papel (si no, la impresión no está al 100 %).', 2.8)
    lx, ly = 112, 38
    g.text(lx, ly, 'Cómo usar esta hoja', 4.0, '#111', 'start', 'bold')
    notas = [
        'El cobre está en ESPEJO: es el que se imprime para la transferencia de tóner (el texto de la página no).',
        'Imprímelo al 100 %, sin escalar, y comprueba la barra de 50 mm antes de transferir.',
        'Cada pad tiene un punto blanco para guiar el taladro. El contorno de trazos es solo la guía de corte de la placa.',
        f'Tamaño mínimo de la placa de cobre: {ancho:.1f} × {y1 - y0:.1f} mm.',
        'Solo debe haber cobre donde la hoja 1 muestra pistas y pads. Revisa los pads por si se unen tras grabar.',
        'Esta hoja es un borrador; no la imprimas para grabar hasta medir las piezas y verificar la hoja 1.',
    ]
    y = ly + 8
    for n in notas:
        for k, linea in enumerate(textwrap.wrap(n, 52)):
            g.text(lx + (0 if k == 0 else 3), y, ('• ' if k == 0 else '') + linea, 2.8)
            y += 3.7
        y += 1.2
    return g


def hoja_datos(resultados):
    g = Pag()
    cabecera(g, 'Taladros, puente de cable, comprobaciones y pendientes', 3)
    y = 34

    def titulo(t, color='#111'):
        nonlocal y
        g.text(15, y, t, 4.0, color, 'start', 'bold')
        y += 6

    def lineas(textos, ancho=118, size=2.9, x=15):
        nonlocal y
        for t in textos:
            for k, linea in enumerate(textwrap.wrap(t, ancho)):
                g.text(x + (0 if k == 0 else 3), y, ('• ' if k == 0 else '') + linea, size)
                y += 3.9
            y += 0.8
        y += 3

    grupos = defaultdict(list)
    for q in PADS.values():
        grupos[(q['d'], q['drill'])].append(q['ref'])
    titulo('Taladros (pads y brocas)')
    g.text(15, y, 'Pad Ø', 2.9, '#111', 'start', 'bold')
    g.text(40, y, 'Broca', 2.9, '#111', 'start', 'bold')
    g.text(62, y, 'Pads', 2.9, '#111', 'start', 'bold')
    g.text(80, y, 'Piezas', 2.9, '#111', 'start', 'bold')
    y += 4.5
    for (d, br), refs in sorted(grupos.items()):
        cuenta = len(refs)
        piezas = ', '.join(sorted(set(refs), key=lambda r: (r[0], int(''.join(ch for ch in r if ch.isdigit())))))
        g.text(15, y, f'{d:.1f} mm', 2.9)
        g.text(40, y, f'{br:.1f} mm', 2.9)
        g.text(62, y, str(cuenta), 2.9)
        for k, linea in enumerate(textwrap.wrap(piezas, 70)):
            g.text(80, y + k * 3.9, linea, 2.9)
        y += max(1, len(textwrap.wrap(piezas, 70))) * 3.9 + 1
    y += 2
    lineas(['Las brocas son valores de partida: ajústalas al grosor de las patas de tus piezas (TO-220, 1N5819, bornes y zócalos). Mide antes de taladrar.'])
    titulo('Puente de cable (1 unidad)')
    a, b = PADS[('W1', '1')], PADS[('W1', '2')]
    lineas([f'W1: entre los pads W1.1 y W1.2 ({math.hypot(a["x"] - b["x"], a["y"] - b["y"]):.2f} mm), alambre AISLADO o con funda, por encima de la pista de GPIO26. '
            'Es la unión de GND entre la parte oeste (J1, J2 y etapa del cooler) y la parte este (A14, J3, etapa de la bomba y entrada de 12 V). '
            'Por W1 vuelve la corriente del cooler (sin medir): usa alambre de cobre de 0,5 mm o más y mide la corriente real del cooler antes de usar la placa.'])
    titulo('Comprobaciones del script (sobre el papel)')
    for ok, msg in resultados:
        for k, linea in enumerate(textwrap.wrap(msg, 118)):
            g.text(15, y, ('OK  ' if ok else 'FALLO ') + linea if k == 0 else '      ' + linea, 2.8, '#14532d' if ok else '#b00020')
            y += 3.7
    y += 3
    g.text(15, y, 'Estas comprobaciones salen de la geometría dibujada; no sustituyen una revisión del cobre real, una medición ni una prueba física.',
           2.8, '#b00020')
    y += 8
    titulo('Supuestos y datos pendientes', '#b00020')
    lineas([
        f'Distancia entre filas del NodeMCU-32S: {FILA_MM:.1f} mm PROVISIONAL (medir centro a centro entre los pines de cada fila).',
        'Orientación del ESP32 con USB a la derecha: supuesto a verificar con la placa (ver hoja 1). Si estuviera invertida, el trazado no sirve.',
        f'Paso de bornes de tornillo {PASO_BORNE_MM:.2f} mm PROVISIONAL; también el tamaño real de sus pads y su taladro (3,0 / 1,3 mm de partida).',
        'Orden de pines del módulo DHT11 y del sensor de suelo, y polaridad de la bomba y del cooler: siguen sin verificar (ver el esquemático).',
        'Fusible: sin formato elegido; el trazado deja dos pads para un portafusible con cables.',
        'Pads de 2,0 mm con taladro 1,0 mm y pistas de 0,8 / 2,0 mm: reglas de la hoja 4 del esquemático, no probadas con tu método de grabado.',
        'La separación de 0,5 mm entre redes depende de la calidad de tu transferencia de tóner; si no la logras, hay que rehacer el trazado con más holgura.',
        'Con polaridad de la fuente invertida se quemaría el fusible y se podría dañar C1 (ver hoja 4 del esquemático). Marca + y − en J4.',
    ], 118, 2.9)
    return g


def main():
    resultados, fallos = verificar()
    if fallos:
        print('HAY FALLOS:', fallos)
        return 1
    paginas = [hoja_componentes(), hoja_cobre(), hoja_datos(resultados)]
    with tempfile.TemporaryDirectory() as tmp:
        pdfs = []
        for i, pag in enumerate(paginas, 1):
            destino = os.path.join(tmp, f'p{i}.pdf')
            cairosvg.svg2pdf(bytestring=pag.svg().encode('utf-8'), write_to=destino)
            pdfs.append(destino)
        subprocess.run(['pdfunite', *pdfs, SALIDA], check=True)
    print('TODO OK (sobre el papel):', SALIDA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
