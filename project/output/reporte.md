# Reporte de Encuestas Mensuales

## Contexto

- **Fuente:** Excels mensuales `encuestas_YYYYMM.xlsx`

- **Periodo:** 2025-01-11 — 2025-12-12

- **Actualización:** batch semanal

- **Trazabilidad:** `_ingest_ts`, `_source_file`, `_batch_id`


## KPIs

- **Encuestas (clean):** 1838

- **NS/NC:** 227 (12.4%)

- **Media de satisfacción:** 5.41


### Definiciones de KPI

- **Encuestas (clean):** nº de filas tras reglas de calidad (fechas válidas, satisfacción 1–10, id_respuesta presente).

- **NS/NC:** recuento de filas con `satisfaccion` nula tras mapear valores como 'no sabe/no contesta'.

- **Media de satisfacción:** media aritmética de `satisfaccion` (1–10), excluyendo nulos.

- **Evolución mensual:** `count` y `mean` por mes de `fecha`.


## Distribución de satisfacción (1–10 + NS/NC)

| satisf_str   |   n |
|:-------------|----:|
| 1            | 167 |
| 2            | 171 |
| 3            | 180 |
| 4            | 153 |
| 5            | 156 |
| 6            | 136 |
| 7            | 180 |
| 8            | 169 |
| 9            | 150 |
| 10           | 149 |
| NS/NC        | 227 |



## Evolución mensual

| mes                 |   encuestas |   media_satisf |
|:--------------------|------------:|---------------:|
| 2025-01-01 00:00:00 |         195 |           5.43 |
| 2025-02-01 00:00:00 |         148 |           5.7  |
| 2025-03-01 00:00:00 |         142 |           5.48 |
| 2025-04-01 00:00:00 |         139 |           5.13 |
| 2025-05-01 00:00:00 |         145 |           5.57 |
| 2025-06-01 00:00:00 |         134 |           5.45 |
| 2025-07-01 00:00:00 |         139 |           5.06 |
| 2025-08-01 00:00:00 |         158 |           5.37 |
| 2025-09-01 00:00:00 |         143 |           5.58 |
| 2025-10-01 00:00:00 |         185 |           5.37 |
| 2025-11-01 00:00:00 |         155 |           5.35 |
| 2025-12-01 00:00:00 |         155 |           5.35 |



## Quarantine (resumen)

| causa                             |    n |
|:----------------------------------|-----:|
| fecha_invalida                    | 2906 |
| fecha_invalida;satisf_fuera_rango |  165 |
| satisf_fuera_rango                |   91 |