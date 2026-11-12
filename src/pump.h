#pragma once
#include <Arduino.h>

// Bomba de agua controlada por un MOSFET (GPIO26 -> compuerta). Sin flotador: la bomba
// se apaga sola tras PUMP_MAX_ON_MS como proteccion contra marcha en seco.
void pumpBegin();
void pumpStart();      // enciende; se apagara sola al cumplirse el tiempo maximo
void pumpStop();
void pumpUpdate();     // llamar en cada vuelta del loop
bool pumpIsOn();
