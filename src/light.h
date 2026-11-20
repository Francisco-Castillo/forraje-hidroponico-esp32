#pragma once
#include <Arduino.h>

// Luz de cultivo en GPIO25 (salida digital; la etapa de potencia aun no esta elegida).
// Modo automatico: encendida de LIGHT_ON_HOUR a LIGHT_OFF_HOUR (hora local, ventana que
// cruza la medianoche). Sin hora valida (sin NTP) queda apagada. Modo manual: ignora el
// horario hasta volver al automatico.
void lightBegin();
void lightUpdate();         // llamar en cada vuelta del loop
void lightToggleManual();   // automatico -> manual (estado invertido) -> automatico
bool lightIsOn();
bool lightIsManual();
