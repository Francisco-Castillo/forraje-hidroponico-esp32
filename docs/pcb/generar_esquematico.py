#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera docs/pcb/esquematico-pcb.pdf (esquematico y datos para la PCB casera).

Requisitos: python3, cairosvg (pip install cairosvg) y pdfunite (paquete poppler-utils).
Uso:        python3 docs/pcb/generar_esquematico.py

La lista CONEXIONES es la fuente de las redes: de ella salen las etiquetas de los pines
dibujados, la tabla de redes del PDF y las comprobaciones de verificar(). Los cables internos
de las etapas de potencia (bomba y cooler) se dibujan a mano: revisalos sobre el dibujo.
"""
import html
import os
import subprocess
import sys
import tempfile
import textwrap
from collections import defaultdict

import cairosvg

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, 'esquematico-pcb.pdf')
W, H = 1122, 794                      # A4 apaisado a 96 dpi
FUENTE = 'Arial, Helvetica, sans-serif'
FECHA = '2026-11-12'
TOTAL_HOJAS = 4

# ---------------------------------------------------------------- datos del circuito
# (referencia, pin, red)
CONEXIONES = [
    # ESP32 NodeMCU-32S en zocalos. Fila A empieza en 3V3 y termina en 5V; fila B empieza en GND y termina en CLK
    ('U1', 'A1', '+3V3'), ('U1', 'A14', 'GND'), ('U1', 'B13', 'GPIO4'), ('U1', 'A5', 'GPIO34'),
    ('U1', 'A11', 'GPIO27'), ('U1', 'A10', 'GPIO26'), ('U1', 'B11', 'GPIO17'),
    # sensores
    ('J1', '1', '+3V3'), ('J1', '2', 'GPIO4'), ('J1', '3', 'GND'),
    ('J2', '1', 'GND'), ('J2', '2', '+3V3'), ('J2', '3', 'GPIO34'),
    ('J3', '1', 'GPIO27'), ('J3', '2', 'GND'),
    # entrada de 12 V
    ('J4', '1', '12V_IN'), ('J4', '2', 'GND'),
    ('F1', '1', '12V_IN'), ('F1', '2', '+12V'),
    ('C1', '+', '+12V'), ('C1', '-', 'GND'),
    # etapa de la bomba
    ('J5', '1', '+12V'), ('J5', '2', 'DRENADOR_BOMBA'),
    ('Q1', 'G', 'GATE_BOMBA'), ('Q1', 'D', 'DRENADOR_BOMBA'), ('Q1', 'S', 'GND'),
    ('R1', '1', 'GPIO26'), ('R1', '2', 'GATE_BOMBA'),
    ('R2', '1', 'GATE_BOMBA'), ('R2', '2', 'GND'),
    ('D1', 'K', '+12V'), ('D1', 'A', 'DRENADOR_BOMBA'),
    # etapa del cooler
    ('J6', '1', '+12V'), ('J6', '2', 'DRENADOR_COOLER'),
    ('Q2', 'G', 'GATE_COOLER'), ('Q2', 'D', 'DRENADOR_COOLER'), ('Q2', 'S', 'GND'),
    ('R3', '1', 'GPIO17'), ('R3', '2', 'GATE_COOLER'),
    ('R4', '1', 'GATE_COOLER'), ('R4', '2', 'GND'),
    ('D2', 'K', '+12V'), ('D2', 'A', 'DRENADOR_COOLER'),
]
NET = {(r, p): n for r, p, n in CONEXIONES}

# pin de la placa -> rotulo del serigrafiado (hardware-inventory.md)
U1_ROTULO = {'A1': '3V3', 'A14': 'GND', 'B13': 'P4', 'A5': 'P34', 'A11': 'P27', 'A10': 'P26', 'B11': 'P17'}
U1_PROHIBIDOS = {'P0', 'P2', 'P12', 'P15', 'SD0', 'SD1', 'SD2', 'SD3', 'CLK', 'TX', 'RX', 'EN'}

NETCOL = {'+3V3': '#d62828', '+12V': '#9d0208', '12V_IN': '#9d0208', 'GND': '#222222',
          'GPIO4': '#b58900', 'GPIO34': '#2e9e4f', 'GPIO27': '#8b5cf6', 'GPIO26': '#f97316',
          'GPIO17': '#0d9488'}

# lista de materiales: (refs, cantidad, componente, valor, notas)
BOM = [
    ('U1', '2', 'Zócalo hembra 1x19, paso 2,54 mm (2 unidades, para NodeMCU-32S de 38 pines)', '—',
     'Distancia entre las dos filas de tu placa: PENDIENTE, medirla. Dejar libre el lado del USB.'),
    ('Q1, Q2', '2', 'MOSFET canal N IRLZ44N, TO-220', '—',
     'Patas G, D, S (vista de frente, hoja de datos de Infineon). El montaje actual ya usa dos.'),
    ('R1, R3', '2', 'Resistencia 1/4 W', '220 Ω', 'Limita la corriente de compuerta desde el GPIO.'),
    ('R2, R4', '2', 'Resistencia 1/4 W', '10 kΩ', 'Mantiene el MOSFET apagado mientras el ESP32 arranca.'),
    ('D1, D2', '2', 'Diodo Schottky 1N5819', '—', 'En paralelo con la carga; banda (cátodo) hacia +12 V.'),
    ('C1', '1', 'Capacitor electrolítico', '1000 µF / 25 V', 'Polarizado. Cerca de J4 y de los MOSFET.'),
    ('F1', '1', 'Portafusible + fusible', '3 A', 'Formato del fusible y del portafusible: PENDIENTE de definir.'),
    ('J1', '1', 'Tira de pines 1x3, paso 2,54 mm', '—', 'Módulo DHT11. Orden de pines del módulo: PENDIENTE.'),
    ('J2', '1', 'Tira de pines 1x3, paso 2,54 mm', '—', 'Sensor de suelo. Orden de pines: según el montaje actual, sin verificar.'),
    ('J3', '1', 'Tira de pines 1x2, paso 2,54 mm', '—', 'Flotador de nivel (2 hilos).'),
    ('J4, J5, J6', '3', 'Borne de tornillo de 2 pines', '—',
     'Fuente 12 V, bomba y cooler. Paso (5,0 o 5,08 mm): PENDIENTE, depende del borne que consigas.'),
]

NOTAS_ESQ = [
    'El ESP32 se alimenta solo por su USB (5 V). Los 12 V NUNCA van al ESP32: solo a las cargas. GND comun entre fuente y ESP32.',
    'R2 y R4 mantienen cada MOSFET apagado al arrancar; D1 y D2 absorben el pico inductivo de la bomba y del cooler.',
    'C1 va junto a J4. Los pines del ESP32 que no aparecen no se conectan (5V, EN, P0, P2, P12, P15 y demas).',
    'Datos que faltan antes de construir: orden de pines del DHT11, medida de los zocalos, paso de los bornes y formato del fusible.',
]

# ---------------------------------------------------------------- dibujo
class Hoja:
    def __init__(self):
        self.e = []

    def add(self, s):
        self.e.append(s)

    def text(self, x, y, t, size=10, fill='#111', anchor='start', weight='normal'):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" font-family="{FUENTE}">{html.escape(t, quote=False)}</text>')

    def line(self, x1, y1, x2, y2, color='#111', w=1.6):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')

    def rect(self, x, y, w, h, fill='none', stroke='#111', sw=1.4, rx=0):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def circ(self, x, y, r, fill='#111', stroke='none'):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')

    def poly(self, pts, fill='#111', stroke='none', sw=1):
        p = ' '.join(f'{x},{y}' for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d, stroke='#111', w=1.6, fill='none'):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 {W} {H}">'
                f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + ''.join(self.e) + '</svg>')


ETIQUETADOS = set()


def flag(h, x, y, net, lado='r'):
    col = NETCOL[net]
    tw = len(net) * 6.4 + 10
    s = 1 if lado == 'r' else -1
    h.line(x, y, x + 12 * s, y)
    h.poly([(x + 12 * s, y), (x + 19 * s, y - 8), (x + (19 + tw) * s, y - 8),
            (x + (19 + tw) * s, y + 8), (x + 19 * s, y + 8)], col)
    h.text(x + (19 + tw / 2) * s, y + 4, net, 10, '#fff', 'middle', 'bold')


def pin_flag(h, ref, pin, x, y, lado='r'):
    ETIQUETADOS.add((ref, pin))
    flag(h, x, y, NET[(ref, pin)], lado)


def tierra(h, x, y):
    h.line(x, y, x, y + 6)
    h.line(x - 9, y + 6, x + 9, y + 6)
    h.line(x - 5.5, y + 10, x + 5.5, y + 10)
    h.line(x - 2, y + 14, x + 2, y + 14)


def potencia(h, x, y, txt):
    h.line(x, y, x, y - 14)
    h.line(x - 9, y - 14, x + 9, y - 14, '#9d0208', 2.4)
    h.text(x, y - 19, txt, 10, '#9d0208', 'middle', 'bold')


def resistencia_h(h, x1, x2, y):
    xm = (x1 + x2) / 2
    h.line(x1, y, xm - 15, y)
    h.line(xm + 15, y, x2, y)
    h.rect(xm - 15, y - 5, 30, 10, '#fff')


def resistencia_v(h, x, y1, y2):
    ym = (y1 + y2) / 2
    h.line(x, y1, x, ym - 15)
    h.line(x, ym + 15, x, y2)
    h.rect(x - 5, ym - 15, 10, 30, '#fff')


def diodo_v(h, x, y1, y2):
    """Catodo arriba (y1), anodo abajo (y2)."""
    cy = (y1 + y2) / 2
    h.line(x, y1, x, cy - 6)
    h.line(x, cy + 8, x, y2)
    h.poly([(x - 7, cy + 8), (x + 7, cy + 8), (x, cy - 6)], '#fff', '#111', 1.4)
    h.line(x - 8, cy - 6, x + 8, cy - 6, '#111', 2.2)


def punto(h, x, y):
    h.circ(x, y, 3)


def caja_conector(h, x, y, ancho, titulo, pines, nota=None):
    """Tira de pines con los pines a la derecha. pines: [(ref, pin, texto_interior)]"""
    alto = 14 + 20 * len(pines)
    h.text(x, y - 8, titulo, 11, '#111', 'start', 'bold')
    h.rect(x, y, ancho, alto, '#f8fafc')
    for i, (ref, pin, txt) in enumerate(pines):
        py = y + 18 + 20 * i
        h.text(x + 8, py + 3.5, txt, 10)
        h.rect(x + ancho - 4, py - 4, 8, 8, '#d4af37', '#111', 1)
        pin_flag(h, ref, pin, x + ancho + 4, py)
    if nota:
        h.text(x, y + alto + 14, nota, 9, '#b00020', 'start', 'bold')


def mosfet(h, qx, oy, ref, valor):
    """Drenador en (qx, oy+150), fuente a tierra en (qx, oy+265); compuerta en (qx-30, oy+215)."""
    h.line(qx, oy + 150, qx, oy + 190)                                    # drenador
    h.line(qx - 6, oy + 190, qx, oy + 190)
    h.line(qx - 6, oy + 240, qx, oy + 240)                                # fuente
    h.line(qx, oy + 240, qx, oy + 265)
    for a, b in ((183, 197), (205, 225), (233, 247)):                     # canal
        h.line(qx - 6, oy + a, qx - 6, oy + b, '#111', 2.4)
    h.line(qx - 12, oy + 183, qx - 12, oy + 247, '#111', 2.4)             # placa de la compuerta
    h.line(qx - 30, oy + 215, qx - 12, oy + 215)
    h.line(qx - 6, oy + 215, qx, oy + 215)
    h.line(qx, oy + 215, qx, oy + 240)                                    # sustrato a la fuente
    h.poly([(qx - 6, oy + 215), (qx + 1, oy + 211), (qx + 1, oy + 219)], '#111')  # flecha canal N
    h.text(qx + 12, oy + 210, ref, 11, '#111', 'start', 'bold')
    h.text(qx + 12, oy + 223, valor, 10)
    h.text(qx + 12, oy + 235, 'G · D · S', 9, '#555')


def etapa(h, ox, oy, n_r_gate, n_r_pd, n_diodo, n_q, n_j, gpio_r, titulo, carga, pines_carga, nota_carga):
    """Etapa de potencia (MOSFET de lado bajo). ox, oy: origen; ver comentarios de coordenadas."""
    vx, lx, qx = ox + 40, ox + 100, ox + 70
    h.text(ox - 126, oy - 24, titulo, 12, '#111', 'start', 'bold')
    # riel +12 V
    h.line(vx, oy + 30, lx, oy + 30)
    punto(h, qx, oy + 30)
    potencia(h, qx, oy + 30, '+12V')
    # diodo D (catodo arriba) entre el riel y el drenador
    h.line(vx, oy + 30, vx, oy + 70)
    diodo_v(h, vx, oy + 70, oy + 110)
    h.line(vx, oy + 110, vx, oy + 150)
    h.text(vx - 10, oy + 86, n_diodo, 11, '#111', 'end', 'bold')
    h.text(vx - 10, oy + 99, '1N5819', 10, '#111', 'end')
    h.text(vx - 10, oy + 111, 'banda arriba', 9, '#555', 'end')
    # carga (borne de tornillo J)
    h.line(lx, oy + 30, lx, oy + 75)
    h.rect(lx - 12, oy + 62, 24, 56, '#f8fafc')
    h.circ(lx, oy + 75, 5, '#fff', '#111')
    h.circ(lx, oy + 105, 5, '#fff', '#111')
    h.line(lx, oy + 105, lx, oy + 150)
    h.text(lx + 18, oy + 72, n_j, 11, '#111', 'start', 'bold')
    h.text(lx + 18, oy + 85, carga, 10)
    h.text(lx + 18, oy + 98, pines_carga[0], 9, '#555')
    h.text(lx + 18, oy + 110, pines_carga[1], 9, '#555')
    h.text(lx + 18, oy + 122, nota_carga, 9, '#b00020')
    # nodo drenador
    h.line(vx, oy + 150, lx, oy + 150)
    punto(h, qx, oy + 150)
    punto(h, vx, oy + 150)
    punto(h, lx, oy + 150)
    h.text(lx + 18, oy + 158, 'drenador', 9, '#555')
    mosfet(h, qx, oy, n_q, 'IRLZ44N')
    tierra(h, qx, oy + 265)
    # compuerta: GPIO -> R(220) -> compuerta, R(10k) a tierra
    gx = ox + 5
    pin_flag(h, n_r_gate, '1', ox - 60, oy + 215, 'l')
    resistencia_h(h, ox - 60, gx, oy + 215)
    h.line(gx, oy + 215, qx - 30, oy + 215)
    punto(h, gx, oy + 215)
    h.text(ox - 37, oy + 203, n_r_gate, 10, '#111', 'middle', 'bold')
    h.text(ox - 37, oy + 238, '220 Ω', 10, '#111', 'middle')
    resistencia_v(h, gx, oy + 215, oy + 285)
    tierra(h, gx, oy + 285)
    h.text(gx + 10, oy + 246, n_r_pd, 10, '#111', 'start', 'bold')
    h.text(gx + 10, oy + 259, '10 kΩ', 10)
    h.text(gx + 10, oy + 271, 'a tierra', 9, '#555')


def hoja_esquema():
    h = Hoja()
    h.text(30, 32, 'Esquemático: ESP32 + sensores + bomba + cooler (PCB casera de una cara)', 19, '#111', 'start', 'bold')
    h.text(30, 52, 'BORRADOR sobre el papel: la PCB no está construida ni probada. Los datos marcados PENDIENTE no están verificados.',
           11, '#b00020')
    # ---- U1
    h.rect(40, 95, 210, 250, '#f8fafc', '#111', 1.8, 3)
    h.text(145, 88, 'U1 · ESP32 NodeMCU-32S (en zócalos)', 11, '#111', 'middle', 'bold')
    filas = [('A1', '3V3', 130), ('A14', 'GND', 160), ('B13', 'P4  (GPIO4)', 190), ('A5', 'P34 (GPIO34)', 220),
             ('A11', 'P27 (GPIO27)', 250), ('A10', 'P26 (GPIO26)', 280), ('B11', 'P17 (GPIO17)', 310)]
    for pin, nombre, y in filas:
        h.text(244, y + 3.5, f'{nombre} · {pin}', 10, '#111', 'end')
        h.rect(246, y - 4, 8, 8, '#d4af37', '#111', 1)
        pin_flag(h, 'U1', pin, 254, y)
    h.text(50, 118, 'Fila A: 3V3 … 5V · Fila B: GND … CLK', 9, '#555')
    h.text(50, 333, 'USB (5 V) alimenta la placa; 5V sin usar', 9, '#555')
    # ---- sensores
    caja_conector(h, 360, 110, 120, 'J1 · DHT11 (módulo, 3 pines)',
                  [('J1', '1', '1  + (alim.)'), ('J1', '2', '2  OUT (datos)'), ('J1', '3', '3  − (GND)')],
                  'Orden de pines: PENDIENTE de verificar')
    caja_conector(h, 620, 110, 120, 'J2 · Sensor de suelo capacitivo',
                  [('J2', '1', '1  GND'), ('J2', '2', '2  VCC'), ('J2', '3', '3  AOUT')],
                  'Orden y rango de AOUT: PENDIENTES')
    caja_conector(h, 880, 110, 110, 'J3 · Flotador de nivel',
                  [('J3', '1', '1  hilo 1'), ('J3', '2', '2  hilo 2')],
                  'Se asume interruptor sin polaridad')
    h.text(880, 214, 'Sin firmware todavía', 9, '#555')
    # ---- entrada de 12 V
    sy = 395
    h.text(40, sy - 6, 'Entrada de 12 V (fuente de 12 V / 3 A)', 11, '#111', 'start', 'bold')
    h.rect(50, sy + 14, 24, 56, '#f8fafc')
    h.circ(62, sy + 30, 5, '#fff', '#111')
    h.circ(62, sy + 56, 5, '#fff', '#111')
    h.text(50, sy + 140, 'J4: 1 = +12 V, 2 = GND (borne de tornillo)', 9, '#555')
    h.line(62, sy + 30, 128, sy + 30)
    h.text(84, sy + 22, '12V_IN', 9, '#9d0208', 'start', 'bold')
    h.rect(128, sy + 24, 40, 12, '#fff')
    h.line(128, sy + 30, 168, sy + 30)
    h.text(148, sy + 52, 'F1  3 A', 10, '#111', 'middle', 'bold')
    h.line(168, sy + 30, 210, sy + 30)
    punto(h, 200, sy + 30)
    flag(h, 210, sy + 30, '+12V', 'r')
    h.line(200, sy + 30, 200, sy + 70)                                   # C1
    h.line(190, sy + 70, 210, sy + 70, '#111', 2.4)
    h.path(f'M190,{sy+80} Q200,{sy+75} 210,{sy+80}', '#111', 2.4)
    h.line(200, sy + 78, 200, sy + 110)
    tierra(h, 200, sy + 110)
    h.text(216, sy + 74, '+', 11, '#9d0208', 'start', 'bold')
    h.text(222, sy + 92, 'C1  1000 µF / 25 V', 10, '#111', 'start', 'bold')
    h.text(222, sy + 105, '(pata larga = +)', 9, '#555')
    h.line(62, sy + 56, 100, sy + 56)
    h.line(100, sy + 56, 100, sy + 110)
    tierra(h, 100, sy + 110)
    # ---- etapas
    etapa(h, 460, 385, 'R1', 'R2', 'D1', 'Q1', 'J5', 'GPIO26', 'Etapa de la bomba (GPIO26)',
          'Bomba JT500', ('1  + (marrón*)', '2  − (azul*)'), '* color sin confirmar')
    etapa(h, 800, 385, 'R3', 'R4', 'D2', 'Q2', 'J6', 'GPIO17', 'Etapa del cooler (GPIO17)',
          'Cooler 12 V', ('1  + (blanco*)', '2  − (negro*)'), '* polaridad sin leer')
    # ---- notas y cuadro de rotulacion
    h.text(40, 712, 'Notas de diseño', 11, '#111', 'start', 'bold')
    for i, n in enumerate(NOTAS_ESQ):
        for j, linea in enumerate(textwrap.wrap(n, 150)):
            h.text(40, 727 + i * 14 + j * 0, '• ' + linea if j == 0 else linea, 9.5)
    h.rect(800, 690, 290, 84, '#fff', '#111', 1.4)
    h.text(810, 708, 'Esquemático ESP32 + bomba + cooler', 11, '#111', 'start', 'bold')
    h.text(810, 724, 'PCB casera, una cara · hoja 1 de %d' % TOTAL_HOJAS, 10)
    h.text(810, 740, f'Fecha {FECHA} · Rev. 0 (borrador)', 10)
    h.text(810, 758, 'SIN CONSTRUIR NI PROBAR', 10, '#b00020', 'start', 'bold')
    return h


def ajustar(texto, ancho_px, size):
    return textwrap.wrap(texto, max(10, int(ancho_px / (size * 0.52))))


def tabla(h, x, y, cols, filas, size=10, alto_min=20):
    """cols: [(titulo, ancho)]. Devuelve la y final."""
    ancho = sum(c[1] for c in cols)
    h.rect(x, y, ancho, 22, '#e2e8f0', '#94a3b8', 1)
    cx = x
    for t, w in cols:
        h.text(cx + 6, y + 15, t, size, '#111', 'start', 'bold')
        cx += w
    y += 22
    for fila in filas:
        celdas = [ajustar(str(c), w - 10, size) or [''] for c, (_, w) in zip(fila, cols)]
        n = max(len(c) for c in celdas)
        alto = max(alto_min, 8 + n * (size + 3))
        h.rect(x, y, ancho, alto, '#fff', '#cbd5e1', 1)
        cx = x
        for c, (_, w) in zip(celdas, cols):
            for k, linea in enumerate(c):
                h.text(cx + 6, y + 14 + k * (size + 3), linea, size)
            cx += w
        y += alto
    return y


def cabecera(h, titulo, n):
    h.text(30, 32, titulo, 18, '#111', 'start', 'bold')
    h.text(30, 50, 'BORRADOR sobre el papel: sin construir ni probar.', 11, '#b00020')
    h.text(1092, 780, f'Hoja {n} de {TOTAL_HOJAS} · {FECHA}', 9, '#555', 'end')


def redes():
    r = defaultdict(list)
    for ref, pin, net in CONEXIONES:
        r[net].append(f'{ref}.{pin}')
    return r


def hoja_materiales():
    h = Hoja()
    cabecera(h, 'Lista de materiales y pines del ESP32', 2)
    y = tabla(h, 30, 70, [('Ref.', 90), ('Cant.', 50), ('Componente', 330), ('Valor', 110), ('Notas', 482)],
              BOM, 10)
    h.text(30, y + 26, 'Pines usados del ESP32 NodeMCU-32S', 12, '#111', 'start', 'bold')
    h.text(30, y + 41, 'Posición según el orden del inventario (hardware-inventory.md): fila A empieza en 3V3, fila B empieza en GND.',
           9.5, '#555')
    filas = [
        ('A1', '3V3', '—', '+3V3', 'Alimenta DHT11 y sensor de suelo (3,3 V).'),
        ('A14', 'GND', '—', 'GND', 'El GND junto a P13/P12. El rotulado dudoso junto a 5V no se usa.'),
        ('B13', 'P4', 'GPIO4', 'DHT11 (datos)', 'Junto a P0 y P2 (pines de arranque): no pasar pistas ni cables de P0/P2 por ahí.'),
        ('A5', 'P34', 'GPIO34', 'Sensor de suelo (AOUT)', 'Solo entrada y ADC1.'),
        ('A11', 'P27', 'GPIO27', 'Flotador', 'Entrada con pull-up interno (sin firmware aún).'),
        ('A10', 'P26', 'GPIO26', 'Bomba (compuerta, vía R1)', 'Salida; en firmware src/pump.cpp.'),
        ('B11', 'P17', 'GPIO17', 'Cooler (compuerta, vía R3)', 'Salida; en firmware src/cooler.cpp.'),
    ]
    tabla(h, 30, y + 52, [('Pin', 60), ('Rótulo', 80), ('GPIO', 90), ('Uso', 230), ('Notas', 602)], filas, 10)
    return h


def hoja_conexiones():
    h = Hoja()
    cabecera(h, 'Conectores y lista de redes', 3)
    filas = [
        ('J1', 'Tira 1x3', '1: +3V3 · 2: GPIO4 (datos) · 3: GND', 'Módulo DHT11. Orden de pines del módulo: PENDIENTE.'),
        ('J2', 'Tira 1x3', '1: GND · 2: +3V3 · 3: GPIO34 (AOUT)', 'Sensor de suelo. Orden y rango de AOUT: PENDIENTES.'),
        ('J3', 'Tira 1x2', '1: GPIO27 · 2: GND', 'Flotador (2 hilos). Se asume interruptor sin polaridad.'),
        ('J4', 'Borne 2 pines', '1: +12 V (vía F1) · 2: GND', 'Fuente de 12 V / 3 A. Marcar + y − en la serigrafía.'),
        ('J5', 'Borne 2 pines', '1: +12 V · 2: drenador de Q1', 'Bomba JT500: marrón (+) y azul (−) según el vendedor, sin confirmar.'),
        ('J6', 'Borne 2 pines', '1: +12 V · 2: drenador de Q2', 'Cooler 12 V: blanco (+) y negro (−), funciona así en el montaje; no se leyó en su etiqueta.'),
    ]
    y = tabla(h, 30, 70, [('Ref.', 50), ('Tipo', 120), ('Pines', 380), ('Notas', 512)], filas, 10)
    h.text(30, y + 28, 'Lista de redes (generada desde las conexiones del script)', 12, '#111', 'start', 'bold')
    orden = ['+3V3', 'GND', '12V_IN', '+12V', 'GPIO4', 'GPIO34', 'GPIO27', 'GPIO26', 'GPIO17',
             'GATE_BOMBA', 'DRENADOR_BOMBA', 'GATE_COOLER', 'DRENADOR_COOLER']
    r = redes()
    assert set(orden) == set(r), set(orden) ^ set(r)
    tabla(h, 30, y + 38, [('Red', 160), ('Conexiones', 902)], [(n, '  '.join(sorted(r[n]))) for n in orden], 10, 18)
    return h


def hoja_notas():
    h = Hoja()
    cabecera(h, 'Notas para construir la PCB casera y revisión electrónica', 4)
    y = 78

    def bloque(titulo, lineas, color='#111'):
        nonlocal y
        h.text(30, y, titulo, 12, color, 'start', 'bold')
        y += 16
        for l in lineas:
            partes = textwrap.wrap(l, 175)
            for k, p in enumerate(partes):
                h.text(40 if k == 0 else 52, y, ('• ' if k == 0 else '') + p, 10)
                y += 13
        y += 8

    bloque('Método y reglas de diseño (una cara, transferencia de tóner)', [
        'Una sola cara de cobre, sin vías: cuando una pista deba cruzar otra, se usa un puente de cable en el lado de componentes.',
        'Ancho de pista de potencia (12V_IN, +12V, drenadores, GND de potencia): ≥ 2 mm. Señal: ≥ 0,5 mm. Separación entre pistas: ≥ 0,5 mm.',
        'Referencia: la fórmula general IPC-2221 (cobre de 35 µm, subida de 10 °C) da ≈ 0,5 mm para 1,5 A y ≈ 1,4 mm para 3 A (el fusible). '
        'Es una estimación, no una medición; por eso se recomienda más ancho.',
        'Pads redondos de Ø ≥ 2 mm. Taladro 0,8 mm para resistencias y diodos; 1,0–1,2 mm para el TO-220 y los bornes (ajustar a tus piezas).',
        'La transferencia de tóner exige imprimir el cobre en espejo. Eso se hace en el siguiente paso (trazado de pistas), no en este PDF.',
    ])
    bloque('Disposición recomendada (para el trazado)', [
        'Separar la zona de potencia (J4, F1, C1, Q1, Q2, D1, D2, J5, J6) de la zona lógica (zócalos del ESP32 y J1–J3).',
        'Que la corriente de las cargas vuelva a J4 por una pista de GND ancha y corta, sin pasar por los pines GND del ESP32 ni de los sensores.',
        'C1 junto a J4; D1 y D2 junto a sus bornes de carga; R2 y R4 junto a las compuertas de sus MOSFET.',
        'Zócalos: medir primero la separación real entre las dos filas de tu placa y dejar libre el lado del USB para el cable.',
        'Serigrafía a mano o etiqueta: marcar + y − en J4, J5 y J6.',
    ])
    bloque('Datos del IRLZ44N (hoja de datos de Infineon, IRLZ44NPbF rev. 2.1)', [
        'Patas (vista de frente, TO-220): Gate, Drain, Source, de izquierda a derecha. VGS(th): 1,0 V mín. – 2,0 V máx. (VDS = VGS, ID = 250 µA).',
        'RDS(on) máx.: 0,022 Ω (10 V, 25 A), 0,025 Ω (5 V, 25 A), 0,035 Ω (4 V, 21 A). A 3,3 V la tabla no da un valor garantizado. VGS máx.: ±16 V.',
        'En la gráfica de transferencia (valores típicos, VDS = 25 V, pulsado, 25 °C) se lee ≈ 20 A a 3 V. Lectura aproximada del gráfico, no un dato garantizado.',
        'Estimación sobre el papel: con 1,25 A y 0,035 Ω la pérdida sería ≈ 0,06 W. A 3,3 V la resistencia será mayor; no se midió.',
        'En hardware: el cooler en Q2 funciona con 3,3 V en la compuerta (observación del usuario). La bomba con este montaje no está probada.',
    ])
    bloque('Resultado de la revisión (skill electronics-review): NO SE PUEDE CONFIRMAR', [
        'La conectividad del esquema es coherente (verificada por script sobre la lista de redes; no sustituye una medición ni una prueba física).',
        'Faltan datos: orden de pines del DHT11, rango de AOUT y orden de pines del sensor de suelo, polaridad de la bomba y del cooler leída en su etiqueta, '
        'corriente real de ambas cargas, medidas de zócalos y bornes, formato del fusible.',
        'Riesgo: no hay protección contra polaridad invertida. Con la fuente al revés conducirían los MOSFET (diodo interno) y D1/D2: se quemaría el fusible, '
        'y C1 (electrolítico) podría dañarse. Añadir protección sería un componente nuevo: queda como mejora para una revisión posterior.',
        'Riesgo: toda la corriente (≈1,5 A previstos, hasta 3 A del fusible) pasa por pistas caseras; hacer una prueba corta y tocar MOSFET y pistas para notar calentamiento.',
        'Agua y electricidad: la PCB y los bornes de 12 V, secos y por encima del balde. Bomba sumergida antes de alimentar; sin firmware de flotador todavía.',
        'Pines del ESP32: P4, P17, P26, P27 y P34 no son de flash ni de USB-serie; P4 está junto a P0/P2 (arranque), cuidar el trazado.',
    ], '#b00020')
    return h


def verificar():
    """Comprobaciones sobre la lista de redes (sobre el papel)."""
    errores = []

    def check(cond, msg):
        print('OK   ' if cond else 'FALLO', msg)
        if not cond:
            errores.append(msg)

    pines = [(r, p) for r, p, _ in CONEXIONES]
    check(len(pines) == len(set(pines)), 'ningun pin aparece en dos redes')
    r = redes()
    check(all(len(v) >= 2 for v in r.values()), 'toda red une al menos dos pines')
    check({ref for ref, _ in pines} == {x.strip() for fila in BOM for x in fila[0].split(',')},
          'los componentes del esquema coinciden con la lista de materiales')
    u1 = {p: n for (ref, p), n in NET.items() if ref == 'U1'}
    check(not any(U1_ROTULO[p] in U1_PROHIBIDOS for p in u1), 'ningun pin usado del ESP32 es de flash, arranque o USB-serie')
    check(not any(n in ('+12V', '12V_IN') for n in u1.values()), 'ningun pin del ESP32 esta en la red de 12 V')
    check(NET[('U1', 'A1')] == '+3V3' and NET[('J1', '1')] == '+3V3' and NET[('J2', '2')] == '+3V3', '3V3 alimenta DHT11 y suelo')
    check(NET[('U1', 'A14')] == 'GND' == NET[('J4', '2')] == NET[('C1', '-')], 'GND del ESP32 y de la fuente son la misma red')
    check(NET[('U1', 'B13')] == NET[('J1', '2')] == 'GPIO4', 'DATA del DHT11 en GPIO4')
    check(NET[('U1', 'A5')] == NET[('J2', '3')] == 'GPIO34', 'AOUT del suelo en GPIO34 (entrada ADC1)')
    check(NET[('U1', 'A11')] == NET[('J3', '1')] == 'GPIO27', 'flotador en GPIO27')
    for q, rg, rp, d, j, gpio, drn, gate in (('Q1', 'R1', 'R2', 'D1', 'J5', 'GPIO26', 'DRENADOR_BOMBA', 'GATE_BOMBA'),
                                              ('Q2', 'R3', 'R4', 'D2', 'J6', 'GPIO17', 'DRENADOR_COOLER', 'GATE_COOLER')):
        check(NET[(rg, '1')] == gpio and NET[(rg, '2')] == gate == NET[(q, 'G')], f'{gpio} llega a la compuerta de {q} solo a traves de {rg}')
        check(NET[(rp, '1')] == gate and NET[(rp, '2')] == 'GND', f'{rp} lleva la compuerta de {q} a GND')
        check(NET[(q, 'S')] == 'GND', f'fuente de {q} a GND')
        check(NET[(q, 'D')] == NET[(d, 'A')] == NET[(j, '2')] == drn, f'drenador de {q} = anodo de {d} = carga (-)')
        check(NET[(d, 'K')] == NET[(j, '1')] == '+12V', f'catodo de {d} y carga (+) en +12 V')
        check(gpio not in ('GPIO34', 'GPIO35', 'GPIO36', 'GPIO39'), f'{gpio} (salida) no es un pin solo de entrada')
    check(NET[('J4', '1')] == NET[('F1', '1')] == '12V_IN' and NET[('F1', '2')] == NET[('C1', '+')] == '+12V',
          'los 12 V pasan por el fusible antes de C1 y las cargas')
    check(len({'GND', '+3V3', '+12V', '12V_IN'}) == 4, 'GND, 3V3, +12 V y entrada de 12 V son redes distintas')
    return errores


def main():
    errores = verificar()
    paginas = [hoja_esquema(), hoja_materiales(), hoja_conexiones(), hoja_notas()]
    pines_etiquetados = ETIQUETADOS
    if not pines_etiquetados <= set(NET):
        errores.append('hay etiquetas dibujadas que no estan en la lista de redes')
    if errores:
        print('HAY FALLOS:', errores)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        pdfs = []
        for i, p in enumerate(paginas, 1):
            destino = os.path.join(tmp, f'p{i}.pdf')
            cairosvg.svg2pdf(bytestring=p.svg().encode('utf-8'), write_to=destino)
            pdfs.append(destino)
        subprocess.run(['pdfunite', *pdfs, SALIDA], check=True)
    print('TODO OK (sobre el papel):', SALIDA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
