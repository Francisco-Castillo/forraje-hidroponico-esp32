#pragma once
#include <Arduino.h>

// Sensor capacitivo de humedad de suelo (salida analogica). Valores crudos: sin calibrar,
// NO son un porcentaje de humedad.
struct MoistureReading {
  uint16_t raw;       // promedio de analogRead (0-4095)
  uint32_t millivolts;  // promedio de analogReadMilliVolts (usa la calibracion de fabrica del ESP32)
};

void moistureBegin();
MoistureReading moistureRead();
