---
name: update-documentation
description: Procedimiento para identificar y actualizar solamente la documentación afectada por un cambio de código, hardware o pruebas. Usar después de implementar o confirmar algo.
---

# Actualización de documentación

1. **Resume el cambio.** Anota qué cambió y qué estado tiene: implementado, verificado (compila) o probado físicamente (confirmado por el usuario).
2. **Localiza lo afectado.** Busca en `CLAUDE.md`, `docs/` y `README` los pasajes que mencionan lo modificado. Las conexiones y componentes viven en `docs/hardware-inventory.md`.
3. **Actualiza solo eso.** Modifica únicamente los pasajes afectados. No reescribas documentos enteros.
4. **Evita duplicados.** Si un dato ya está en otro documento, enlázalo en lugar de copiarlo.
5. **Respeta los estados.** No marques como probado físicamente algo que el usuario no haya confirmado. Lo que no se conozca sigue como **desconocido**.
6. **Comprueba la coherencia.** Verifica que los pines, valores y nombres citados coinciden con `src/` y `platformio.ini`.
7. **Informa.** Lista los archivos de documentación modificados y los datos que siguen pendientes.
