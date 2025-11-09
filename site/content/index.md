---
title: "Pipeline de Encuestas"
description: "Documentación completa del pipeline de encuestas — desde la ingesta y limpieza hasta el reporte final."
---

# Pipeline de Encuestas

Bienvenido 👋  
Este sitio documenta el desarrollo y funcionamiento del **pipeline de encuestas**, un sistema automatizado que transforma archivos de datos brutos en reportes analíticos listos para su revisión.

El objetivo principal es **procesar encuestas de satisfacción**, garantizando calidad, trazabilidad y generación automática de informes.

---

## 🧭 Estructura de la documentación

### 📂 1. Ingesta y Almacenamiento
Explica cómo se **cargan los archivos fuente** (CSV o Excel), cómo se detecta el separador automáticamente, se validan las columnas y se genera un Excel con metadatos y un resumen de calidad.  
Además, detalla la **trazabilidad** (_source_file_, _ingest_ts_, _batch_id_) y el almacenamiento en base de datos SQLite y formato Parquet.

👉 [`Ver sección → Ingesta y Almacenamiento`](docs/1-ingesta-almacenamiento.md)

---

### 🧹 2. Limpieza y Control de Calidad
Describe cómo se normalizan los textos, se corrigen los valores, y se aplican **reglas de validación** (fechas, rangos de satisfacción, IDs válidos).  
Los registros que no cumplen las reglas se mueven automáticamente a una **tabla de cuarentena**, preservando el motivo de su exclusión.

👉 [`Ver sección → Limpieza y Control de Calidad`](docs/2-limpieza-calidad.md)

---

### 📊 3. Modelado y Generación de Reportes
Detalla el proceso de **análisis y generación de KPIs**, con cálculos de medias, porcentajes y evolución temporal.  
Incluye la exportación a **Excel (informe de calidad)** y **Markdown (reporte de resultados)**.

👉 [`Ver sección → Modelado y Generación de Reportes`](docs/3-modelo-reporte.md)

---

### 📈 Reporte Final
Visualiza el informe final de encuestas generado automáticamente a partir del pipeline.  
Incluye métricas clave, distribución de satisfacción, evolución mensual y control de calidad de los datos.

👉 [`Ver reporte → Reporte UT1 · Encuestas de Satisfacción`](reportes/reporte-encuestas.md)

---

## 🧩 Tecnologías utilizadas

- **Python + Pandas** → lectura, limpieza y análisis de datos.  
- **SQLite + Parquet** → persistencia eficiente.  
- **OpenPyXL** → generación de informes Excel con formato automático.  
- **Quartz** → documentación web del proyecto.  

---

## 🧠 Autor

Proyecto académico desarrollado por  
**Leandro Pérez Martínez** — módulo **Big Data Aplicado / UT1 – RA1 (FCT)**  
CIFP Carlos III, Cartagena (Murcia).

---

✳️ *Última actualización: 9 de noviembre de 2025.*
