# project/report.py
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
      - KPIs básicos
      - Distribución de satisfacción (1–10 + NS/NC)
      - Evolución mensual (n° encuestas y media)
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

    # Distribución satisfacción (1..10 + NS/NC)
    dist = (
        df.assign(satisf_str=df["satisfaccion"].astype("Int64").astype("string"))
          .assign(satisf_str=lambda d: d["satisf_str"].fillna("NS/NC"))
          .groupby("satisf_str").size().rename("n").reset_index()
          .sort_values("satisf_str")
    )

    # Evolución mensual
    if "fecha" in df.columns:
        evo = (df.assign(mes=_fmt_month(df["fecha"]))
                 .groupby("mes")
                 .agg(encuestas=("satisfaccion", "size"),
                      media_satisf=("satisfaccion", "mean"))
                 .reset_index())
        # evitar floats feos en markdown
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
    md.append(f"- **Media de satisfacción:** {media_sat:.2f}\n" if media_sat == media_sat else "- **Media de satisfacción:** NA\n")

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
