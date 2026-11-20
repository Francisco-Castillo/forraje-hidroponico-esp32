#pragma once
#include <Arduino.h>

// Sensor capacitivo de humedad de suelo (salida analogica). Valores crudos: sin calibrar,
// NO son un porcentaje de humedad.
struct MoistureReading {
  uint16_t raw;       // promedio de analogRead (0-4095)
  uint32_t millivolts;  // promedio de analogReadMilliVolts (usa la calibracion de fabrica del ESP32)
  uint16_t minRaw;    // minimo entre las muestras: junto con maxRaw indica cuanto ruido hubo
  uint16_t maxRaw;    // maximo entre las muestras
  bool valid;         // false si el promedio es 0: el sensor real no llega a 0 V (pin flotando o sin alimentacion)
};

void moistureBegin();
MoistureReading moistureRead();
