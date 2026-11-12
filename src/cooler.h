#pragma once
#include <Arduino.h>

// Cooler de 12 V controlado por un MOSFET (GPIO17 -> R3 -> compuerta). Solo encendido y
// apagado, sin PWM y sin limite de tiempo.
void coolerBegin();
void coolerOn();
void coolerOff();
bool coolerIsOn();
