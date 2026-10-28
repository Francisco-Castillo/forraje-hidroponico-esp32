---
name: electronics-review
description: Procedimiento para revisar circuitos, conexiones, alimentación y riesgos eléctricos del proyecto ESP32. Usar antes de conectar o cambiar hardware, o cuando se pida validar una conexión.
---

# Revisión electrónica

Sigue estos pasos en orden. Usa `docs/hardware-inventory.md` como fuente de datos y no supongas nada que figure como desconocido.

1. **Alcance.** Indica qué circuito o conexión se revisa y qué cambia respecto a lo ya documentado.
2. **Inventario.** Para cada componente implicado anota modelo, tensión de alimentación, consumo y nivel lógico. Si falta algún dato, regístralo como pendiente.
3. **Pines.** Para cada pin del ESP32 comprueba que no sea de arranque, de flash ni solo de entrada para el uso previsto, y que corresponda a la placa confirmada.
4. **Tensiones.** Compara los niveles lógicos entre componentes (el ESP32 trabaja a 3,3 V). Marca cualquier conexión directa entre niveles distintos.
5. **Alimentación.** Revisa la fuente, su corriente máxima frente al consumo total, y que la masa (GND) sea común.
6. **Potencia.** Para cargas como relés, bombas o motores revisa el elemento de conmutación, los diodos de protección y el aislamiento entre la parte de potencia y el ESP32.
7. **Protecciones y riesgos.** Identifica riesgos de cortocircuito, polaridad invertida, sobrecorriente y, si hay tensión de red o agua, seguridad de las personas.
8. **Resultado.** Entrega una de estas conclusiones:
   - **Sin objeciones con los datos disponibles**, con la lista de lo revisado.
   - **No se puede confirmar**, con la lista de datos que faltan.
   - **Problema detectado**, con la causa y la corrección propuesta.

## Reglas

- No declares seguro un circuito sin datos suficientes de sus componentes y conexiones.
- La revisión es sobre el papel. Indica que no sustituye una medición ni una prueba física.
- Si cambian datos de hardware confirmados, actualiza el inventario con la skill `update-documentation`.
