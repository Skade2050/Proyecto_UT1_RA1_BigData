# Proyecto UT1 RA1 BA – Caso 4 📊 Encuestas Mensuales (Excel → CSV/Parquet)

## 🧩 Contexto
Pipeline de datos en Python para procesar encuestas mensuales almacenadas en formato Excel.  
Cubre todo el flujo **ingesta → limpieza/modelado → almacenamiento → reporte Markdown** siguiendo la estructura base del repositorio oficial `Proyecto_UT1_RA1_BA`.

---
## 🧠 Decisiones y supuestos
Clave natural: id_respuesta.
Se aplica política “último gana” por _ingest_ts.

Trazabilidad: columnas _ingest_ts, _source_file, _batch_id.

Dominios: satisfaccion ∈ [1..10]; textos como “No sabe/No contesta” se tratan como NaN.

Deduplicación: si un id_respuesta aparece repetido, se conserva el más reciente.

Quarantine: filas con fecha inválida o satisfaccion fuera de rango se almacenan en quarantine_encuestas.

Almacenamiento:

raw_encuestas y clean_encuestas en SQLite.

clean_encuestas.parquet para analítica.

Reporte Markdown: incluye KPIs, distribución de satisfacción, evolución mensual y resumen de quarantine.

Extra: informe_de_calidad.xlsx con recuento de nulos y causas de quarantine.

---
## 📊 Salidas principales
project/output/reporte.md – Reporte principal en Markdown.

project/output/reporte.pdf – Versión PDF para entrega.

project/output/informe_de_calidad.xlsx – Recuento de nulos y quarantine.

project/output/clean_encuestas.parquet – Datos limpios para analítica.

---
## 🧾 KPIs principales
Total de encuestas (clean)

Porcentaje de NS/NC

Media de satisfacción

Evolución mensual (media y número de encuestas)

---
## 🧱 Requisitos de entorno
pandas
openpyxl
pyarrow
tabulate

---

## 👨‍💻 Autor
Leandro Pérez Martínez

## ▶️ Cómo ejecutar
```bash
# Crear y activar entorno virtual
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el pipeline completo
python run.py


