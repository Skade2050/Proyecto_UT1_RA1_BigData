---
title: "Reporte UT1 · Encuestas de Satisfacción"
description: "Análisis mensual de encuestas tras limpieza, validación y almacenamiento de datos."
---
# Informe de Encuestas (resumen mensual)

Este documento presenta un resumen claro y comprensible de los resultados obtenidos tras el procesamiento de las encuestas.  
Incluye indicadores clave (KPIs), evolución temporal y control de calidad de los datos.

---

## 1. Datos generales

**Periodo analizado:** 2025-01-11 — 2025-12-12  
**Registros procesados (totales):** 5000  
**Registros válidos (clean):** 1838  
**Registros en cuarentena:** 3162  

> Los datos válidos (clean) cumplen con las reglas de calidad definidas (fechas válidas, satisfacción 1–10, id_respuesta presente).  
> Los registros en cuarentena no superan dichas reglas y se almacenan con su motivo de rechazo.

---

## 2. Resumen rápido

| Indicador                     | Valor  |
|-------------------------------|--------:|
| Encuestas válidas (clean)     | 1838   |
| Respuestas NS/NC (sin valor)  | 227    |
| % NS/NC sobre Clean           | 12.4%  |
| Media de satisfacción (1–10)  | 5.41   |

---

## 3. Interpretación de indicadores

- **Encuestas válidas (clean):** respuestas que pasan las reglas básicas de calidad.  
- **NS/NC:** respuestas sin puntuación de satisfacción (por ejemplo, “no sabe / no contesta”).  
- **% NS/NC:** porcentaje de NS/NC respecto al total de respuestas válidas.  
- **Media de satisfacción:** valor medio de las puntuaciones (1 = muy mala, 10 = muy buena).

---

## 4. Distribución de satisfacción (1–10 + NS/NC)

| valor |  n  |
|-------|----:|
| 1     | 167 |
| 2     | 171 |
| 3     | 180 |
| 4     | 153 |
| 5     | 156 |
| 6     | 136 |
| 7     | 184 |
| 8     | 169 |
| 9     | 153 |
| 10    | 149 |
| NS/NC | 227 |

> Muestra la distribución general de las puntuaciones, permitiendo detectar tendencias o sesgos.

---

## 5. Evolución mensual

| mes               | encuestas | media_satisf |
|-------------------|-----------:|--------------:|
| 2025-01-01 00:00:00 | 195 | 5.43 |
| 2025-02-01 00:00:00 | 148 | 5.7  |
| 2025-03-01 00:00:00 | 149 | 5.48 |
| 2025-04-01 00:00:00 | 155 | 5.13 |
| 2025-05-01 00:00:00 | 145 | 5.57 |
| 2025-06-01 00:00:00 | 134 | 5.45 |
| 2025-07-01 00:00:00 | 139 | 5.06 |
| 2025-08-01 00:00:00 | 148 | 5.37 |
| 2025-09-01 00:00:00 | 185 | 5.38 |
| 2025-10-01 00:00:00 | 185 | 5.37 |
| 2025-11-01 00:00:00 | 183 | 5.35 |
| 2025-12-01 00:00:00 | 155 | 5.35 |

> Permite observar la estabilidad mensual de la media de satisfacción.  
> Se aprecia una media relativamente constante con ligeras variaciones entre 5.3 y 5.7.

---

## 6. Calidad de los datos (cuarentena)

Los registros que no cumplen las reglas de calidad se guardan aparte con su motivo específico:

| causa                                |  n   |
|-------------------------------------|------:|
| fecha_invalida                      | 2906 |
| fecha_invalida;satisf_fuera_rango   | 165  |
| satisf_fuera_rango                  | 91   |

> - **fecha_invalida:** error o ausencia en la fecha.  
> - **satisf_fuera_rango:** puntuación fuera del rango permitido (1–10).  
> - **Combinadas:** varios errores en la misma fila.  
>  
> Estas filas se almacenan en la tabla `quarantine_encuestas` para auditoría y depuración futura.

---

## 7. Conclusiones generales

- La satisfacción media se mantiene estable a lo largo del año (**5.4/10**).  
- El porcentaje de NS/NC es moderado (**12.4%**), lo que sugiere una calidad de respuesta aceptable.  
- La mayoría de las incidencias en cuarentena se deben a **fechas inválidas**, indicando posibles errores de formato o exportación.  
- Recomendación: reforzar la validación previa de fechas y fomentar la respuesta completa en las encuestas.

---

## 8. Persistencia y trazabilidad

- **SQLite (`project/encuestas.db`):**  
  - `raw_encuestas`: datos originales.  
  - `clean_encuestas`: datos limpios.  
  - `quarantine_encuestas`: registros rechazados.  
- **Excel (`project/output/informe_de_calidad.xlsx`)**: resumen de nulos y causas de cuarentena.  
- **Markdown (`project/output/reporte.md`)**.  

> Cada registro contiene campos de trazabilidad: `_source_file`, `_ingest_ts`, `_batch_id`.

---
