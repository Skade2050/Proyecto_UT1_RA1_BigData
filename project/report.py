from __future__ import annotations
from pathlib import Path
import pandas as pd

def _fmt_month(s: pd.Series) -> pd.Series:
    # normaliza a primer día de mes (periodo mensual)
    return pd.to_datetime(s).dt.to_period("M").dt.to_timestamp()

def generate_report(df_clean: pd.DataFrame,
                    df_quarantine: pd.DataFrame,
                    output_path: str = "project/output/reporte.md") -> None:
    """
    Genera reporte Markdown con:
      - KPIs básicos (con definiciones)
      - Distribución de satisfacción (1–10 + NS/NC, orden correcto)
      - Evolución mensual (n° encuestas y media)
      - Resumen de cuarentena por causa
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = df_clean.copy()
    # KPIs
    n_total = len(df)
    n_nsnc = df["satisfaccion"].isna().sum() if "satisfaccion" in df.columns else 0
    p_nsnc = (n_nsnc / n_total * 100) if n_total else 0
    media_sat = float(df["satisfaccion"].mean()) if "satisfaccion" in df.columns else None
    fmin = pd.to_datetime(df["fecha"]).min() if "fecha" in df.columns else None
    fmax = pd.to_datetime(df["fecha"]).max() if "fecha" in df.columns else None

    # Distribución satisfacción (1..10 + NS/NC), ordenada correctamente
    levels = [str(i) for i in range(1, 11)] + ["NS/NC"]
    if "satisfaccion" in df.columns:
        dist_tmp = df["satisfaccion"].astype("Int64").astype("string").fillna("NS/NC")
    else:
        dist_tmp = pd.Series([], dtype="string")
    dist = pd.DataFrame({"satisf_str": dist_tmp})
    dist["satisf_str"] = pd.Categorical(dist["satisf_str"], categories=levels, ordered=True)
    dist = (
        dist.groupby("satisf_str").size().rename("n").reset_index()
        if not dist.empty else pd.DataFrame({"satisf_str": levels, "n": [0]*len(levels)})
    ).sort_values("satisf_str")

    # Evolución mensual
    if "fecha" in df.columns:
        evo = (df.assign(mes=_fmt_month(df["fecha"]))
                 .groupby("mes")
                 .agg(encuestas=("satisfaccion", "size"),
                      media_satisf=("satisfaccion", "mean"))
                 .reset_index())
        evo["media_satisf"] = evo["media_satisf"].round(2)
    else:
        evo = pd.DataFrame(columns=["mes", "encuestas", "media_satisf"])

    # Quarantine resumen
    qresumen = (df_quarantine["_quarantine_reason"]
                .value_counts()
                .rename_axis("causa")
                .reset_index(name="n")) if not df_quarantine.empty else pd.DataFrame(columns=["causa","n"])

    # Construcción del Markdown
    md = []
    md.append("# Reporte de Encuestas Mensuales\n")
    md.append("## Contexto\n")
    md.append("- **Fuente:** Excels mensuales `encuestas_YYYYMM.xlsx`\n")
    md.append("- **Periodo:** {} — {}\n".format(fmin.date() if pd.notna(fmin) else "NA",
                                               fmax.date() if pd.notna(fmax) else "NA"))
    md.append("- **Actualización:** batch semanal\n")
    md.append("- **Trazabilidad:** `_ingest_ts`, `_source_file`, `_batch_id`\n")

    md.append("\n## KPIs\n")
    md.append(f"- **Encuestas (clean):** {n_total}\n")
    md.append(f"- **NS/NC:** {n_nsnc} ({p_nsnc:.1f}%)\n")
    if media_sat is not None and not pd.isna(media_sat):
        md.append(f"- **Media de satisfacción:** {media_sat:.2f}\n")
    else:
        md.append("- **Media de satisfacción:** NA\n")

    md.append("\n### Definiciones de KPI\n")
    md.append("- **Encuestas (clean):** nº de filas tras reglas de calidad (fechas válidas, satisfacción 1–10, id_respuesta presente).\n")
    md.append("- **NS/NC:** recuento de filas con `satisfaccion` nula tras mapear valores como 'no sabe/no contesta'.\n")
    md.append("- **Media de satisfacción:** media aritmética de `satisfaccion` (1–10), excluyendo nulos.\n")
    md.append("- **Evolución mensual:** `count` y `mean` por mes de `fecha`.\n")

    md.append("\n## Distribución de satisfacción (1–10 + NS/NC)\n")
    md.append(dist.to_markdown(index=False))
    md.append("\n")

    md.append("\n## Evolución mensual\n")
    md.append(evo.to_markdown(index=False))
    md.append("\n")

    md.append("\n## Quarantine (resumen)\n")
    if not qresumen.empty:
        md.append(qresumen.to_markdown(index=False))
    else:
        md.append("_Sin filas en cuarentena._")

    out.write_text("\n".join(md), encoding="utf-8")


def export_quality_report(df_clean: pd.DataFrame,
                          df_quarantine: pd.DataFrame,
                          xlsx_path: str = "project/output/informe_de_calidad.xlsx") -> None:
    """
    Extra (caso 4): exporta un Excel con:
      - Nulos por campo (clean)
      - Resumen de quarantine por causa
    """
    Path(xlsx_path).parent.mkdir(parents=True, exist_ok=True)

    # Nulos por campo en clean
    if not df_clean.empty:
        nulos = (df_clean.isna().sum()
                 .rename_axis("campo")
                 .reset_index(name="n_nulos"))
    else:
        nulos = pd.DataFrame(columns=["campo", "n_nulos"])

    # Quarantine por causa
    if not df_quarantine.empty and "_quarantine_reason" in df_quarantine.columns:
        qresumen = (df_quarantine["_quarantine_reason"]
                    .value_counts()
                    .rename_axis("causa")
                    .reset_index(name="n"))
    else:
        qresumen = pd.DataFrame(columns=["causa", "n"])

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        nulos.to_excel(w, sheet_name="nulos_por_campo", index=False)
        qresumen.to_excel(w, sheet_name="quarantine_resumen", index=False)
