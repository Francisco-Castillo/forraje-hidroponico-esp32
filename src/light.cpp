#include "light.h"
#include <time.h>

constexpr uint8_t LIGHT_PIN = 25;
constexpr int LIGHT_ON_HOUR = 20;   // enciende a las 20:00 (hora local)
constexpr int LIGHT_OFF_HOUR = 6;   // apaga a las 06:00 (hora local)
constexpr time_t MIN_VALID_EPOCH = 1704067200;  // 2024-01-01: antes de eso no hay hora NTP

static bool on = false;
static bool manual = false;

static void setLight(bool state) {
  digitalWrite(LIGHT_PIN, state ? HIGH : LOW);
  on = state;
}

// true si la hora local cae dentro de la ventana de encendido (puede cruzar la medianoche).
static bool inWindow(int hour) {
  if (LIGHT_ON_HOUR < LIGHT_OFF_HOUR) return hour >= LIGHT_ON_HOUR && hour < LIGHT_OFF_HOUR;
  return hour >= LIGHT_ON_HOUR || hour < LIGHT_OFF_HOUR;
}

void lightBegin() {
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, LOW);  // apagada al arrancar
}

void lightUpdate() {
  if (manual) return;

  bool want = false;
  time_t now = time(nullptr);
  if (now >= MIN_VALID_EPOCH) {
    struct tm local;
    localtime_r(&now, &local);
    want = inWindow(local.tm_hour);
  } else {
    static bool warned = false;
    if (!warned) {
      Serial.println("Luz: sin hora NTP valida, queda apagada");
      warned = true;
    }
  }

  if (want != on) {
    setLight(want);
    Serial.printf("Luz: %s (horario)\n", want ? "encendida" : "apagada");
  }
}

void lightToggleManual() {
  if (!manual) {
    manual = true;
    setLight(!on);
    Serial.printf("Luz: modo manual, %s\n", on ? "encendida" : "apagada");
  } else {
    manual = false;
    Serial.println("Luz: modo automatico");
    lightUpdate();
  }
}

bool lightIsOn() { return on; }
bool lightIsManual() { return manual; }
