from __future__ import annotations
from pathlib import Path
import pandas as pd

# --- Utilidad sencilla: llevar fechas a "primer día del mes" para agrupar por mes
def _fmt_month(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s).dt.to_period("M").dt.to_timestamp()

def generate_report(
    df_clean: pd.DataFrame,
    df_quarantine: pd.DataFrame,
    output_path: str = "project/output/reporte.md",
) -> None:
    
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = df_clean.copy() if isinstance(df_clean, pd.DataFrame) else pd.DataFrame()
    dq = df_quarantine.copy() if isinstance(df_quarantine, pd.DataFrame) else pd.DataFrame()

    # --- KPIs básicos
    n_clean = len(df)
    n_quar = len(dq)
    total_procesado = n_clean + n_quar

    fmin = pd.to_datetime(df["fecha"]).min() if "fecha" in df.columns and n_clean else None
    fmax = pd.to_datetime(df["fecha"]).max() if "fecha" in df.columns and n_clean else None

    if "satisfaccion" in df.columns and n_clean:
        n_nsnc = df["satisfaccion"].isna().sum()
        p_nsnc = (n_nsnc / n_clean * 100) if n_clean else 0.0
        media_sat = df["satisfaccion"].mean()
    else:
        n_nsnc, p_nsnc, media_sat = 0, 0.0, float("nan")

    # --- Distribución 1..10 + NS/NC (en orden correcto)
    niveles = [str(i) for i in range(1, 11)] + ["NS/NC"]
    if "satisfaccion" in df.columns and n_clean:
        dist_vals = df["satisfaccion"].astype("Int64").astype("string").fillna("NS/NC")
        dist = pd.DataFrame({"valor": dist_vals})
        dist["valor"] = pd.Categorical(dist["valor"], categories=niveles, ordered=True)
        dist = dist.value_counts().rename_axis("valor").reset_index(name="n").sort_values("valor")
    else:
        dist = pd.DataFrame({"valor": niveles, "n": [0] * len(niveles)})

    # --- Evolución por mes
    if "fecha" in df.columns and n_clean:
        evo = (
            df.assign(mes=_fmt_month(df["fecha"]))
              .groupby("mes")
              .agg(encuestas=("satisfaccion", "size"),
                   media_satisf=("satisfaccion", "mean"))
              .reset_index()
        )
        evo["media_satisf"] = evo["media_satisf"].round(2)
    else:
        evo = pd.DataFrame(columns=["mes", "encuestas", "media_satisf"])

    # --- Resumen de cuarentena por causa
    if not dq.empty and "_quarantine_reason" in dq.columns:
        qresumen = (
            dq["_quarantine_reason"]
            .value_counts()
            .rename_axis("causa")
            .reset_index(name="n")
            .sort_values("n", ascending=False)
        )
    else:
        qresumen = pd.DataFrame(columns=["causa", "n"])

    # --- Construcción del Markdown (claro y corto)
    md = []
    md.append("# Informe de Encuestas (resumen sencillo)\n")

    md.append("## 1. ¿Qué datos se han analizado?\n")
    md.append(f"- **Periodo:** {fmin.date() if pd.notna(fmin) else 'NA'} — {fmax.date() if pd.notna(fmax) else 'NA'}\n")
    md.append(f"- **Registros procesados (total):** {total_procesado}\n")
    md.append(f"- **Registros válidos (clean):** {n_clean}\n")
    md.append(f"- **Registros en cuarentena:** {n_quar}\n")

    md.append("\n## 2. Resumen rápido\n")
    kpis = pd.DataFrame(
        [
            ["Encuestas válidas (clean)", n_clean],
            ["Respuestas NS/NC (sin valoración)", n_nsnc],
            ["% NS/NC sobre clean", round(p_nsnc, 1)],
            ["Media de satisfacción (1–10)", round(media_sat, 2) if media_sat == media_sat else "NA"],
        ],
        columns=["Indicador", "Valor"],
    )
    md.append(kpis.to_markdown(index=False))
    md.append("\n")

    md.append("\n## 3. ¿Qué significa cada indicador?\n")
    md.append("- **Encuestas válidas (clean):** respuestas que pasan las reglas básicas de calidad.\n")
    md.append("- **NS/NC:** respuestas sin una puntuación de satisfacción (por ejemplo, 'no sabe/no contesta').\n")
    md.append("- **% NS/NC:** porcentaje de NS/NC respecto a todas las respuestas válidas.\n")
    md.append("- **Media de satisfacción:** media aritmética de las puntuaciones (1 = muy mala, 10 = muy buena).\n")

    md.append("\n## 4. Distribución de satisfacción (1–10 + NS/NC)\n")
    md.append(dist.to_markdown(index=False))
    md.append("\n")

    md.append("\n## 5. Evolución por mes\n")
    if not evo.empty:
        md.append(evo.to_markdown(index=False))
    else:
        md.append("_No hay datos suficientes para la evolución mensual._")
    md.append("\n")

    md.append("\n## 6. Calidad de los datos (cuarentena)\n")
    if not qresumen.empty:
        md.append("Los registros que no cumplen las reglas se guardan aparte con su motivo:\n\n")
        md.append(qresumen.to_markdown(index=False))
    else:
        md.append("_No hay registros en cuarentena en esta ejecución._")
    md.append("\n")

    Path(output_path).write_text("\n".join(md), encoding="utf-8")


def export_quality_report(
    df_clean: pd.DataFrame,
    df_quarantine: pd.DataFrame,
    xlsx_path: str = "project/output/informe_de_calidad.xlsx",
) -> None:
    Path(xlsx_path).parent.mkdir(parents=True, exist_ok=True)

    # Nulos por campo (clean)
    if isinstance(df_clean, pd.DataFrame) and not df_clean.empty:
        nulos = (
            df_clean.isna()
                   .sum()
                   .rename_axis("campo")
                   .reset_index(name="n_nulos")
                   .sort_values("n_nulos", ascending=False)
        )
    else:
        nulos = pd.DataFrame(columns=["campo", "n_nulos"])

    # Cuarentena por causa
    if isinstance(df_quarantine, pd.DataFrame) and not df_quarantine.empty and "_quarantine_reason" in df_quarantine.columns:
        qresumen = (
            df_quarantine["_quarantine_reason"]
                        .value_counts()
                        .rename_axis("causa")
                        .reset_index(name="n")
                        .sort_values("n", ascending=False)
        )
    else:
        qresumen = pd.DataFrame(columns=["causa", "n"])

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        nulos.to_excel(w, sheet_name="nulos_por_campo", index=False)
        qresumen.to_excel(w, sheet_name="quarantine_resumen", index=False)
