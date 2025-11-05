from __future__ import annotations
import pandas as pd
import unicodedata

NSNC_VALUES = {
    "no sabe/no contesta", "ns/nc", "nsnc", "no sabe", "no contesta",
    "no se/no contesta", "no sé/no contesta"
}

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def _norm_text(x):
    if pd.isna(x):
        return x
    s = str(x).strip()
    s = _strip_accents(s).lower()
    return s

def _add_cause(s: str, cause: str) -> str:
    """Concatena causas separadas por ';' sin pegarlas."""
    if not s:
        return cause
    return f"{s};{cause}"

def clean_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df_raw.copy()

    # --- normaliza nombres y trim en todas las columnas texto ---
    df.columns = [str(c).strip().lower() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # --- tipado base ---
    df["fecha"] = pd.to_datetime(df.get("fecha"), errors="coerce")

    # satisfaccion: normalizo, NS/NC -> NaN, a Int64
    if "satisfaccion" in df.columns:
        df["_satisfaccion_norm"] = df["satisfaccion"].apply(_norm_text)
        df.loc[df["_satisfaccion_norm"].isin(NSNC_VALUES), "satisfaccion"] = pd.NA
        df["satisfaccion_num"] = pd.to_numeric(df["satisfaccion"], errors="coerce").astype("Int64")
    else:
        df["satisfaccion_num"] = pd.Series([pd.NA] * len(df), dtype="Int64")

    # --- dedupe: 'último gana' por _ingest_ts ---
    key_cols = [c for c in ["id_respuesta"] if c in df.columns]
    if key_cols:
        sort_cols = list(df.columns.intersection(["_ingest_ts"]))
        if sort_cols:
            df = df.sort_values(sort_cols)
        df = df.drop_duplicates(subset=key_cols, keep="last")

    # --- máscaras de calidad (RECALCULADAS sobre df ya deduplicado) ---
    causa_fecha = df["fecha"].isna()

    if "satisfaccion_num" in df.columns:
        causa_rango = ~(df["satisfaccion_num"].between(1, 10)) & df["satisfaccion_num"].notna()
    else:
        causa_rango = pd.Series([False] * len(df), index=df.index)

    if "id_respuesta" in df.columns:
        causa_id = df["id_respuesta"].isna() | (df["id_respuesta"].astype(str).str.strip() == "")
    else:
        causa_id = pd.Series([True] * len(df), index=df.index)  # si no existe, todo inválido

    quarantine_mask = causa_fecha | causa_rango | causa_id

    # --- construir quarantine con causas bien separadas ---
    quarantine = df.loc[quarantine_mask].copy()
    quarantine["_quarantine_reason"] = ""

    # máscaras reindexadas a quarantine (evita mismatches)
    m_fecha_q  = causa_fecha.reindex(quarantine.index, fill_value=False)
    m_rango_q  = causa_rango.reindex(quarantine.index, fill_value=False)
    m_id_q     = causa_id.reindex(quarantine.index,  fill_value=False)

    quarantine.loc[m_fecha_q, "_quarantine_reason"] = \
        quarantine.loc[m_fecha_q, "_quarantine_reason"].apply(lambda s: _add_cause(s, "fecha_invalida"))
    quarantine.loc[m_rango_q, "_quarantine_reason"] = \
        quarantine.loc[m_rango_q, "_quarantine_reason"].apply(lambda s: _add_cause(s, "satisf_fuera_rango"))
    quarantine.loc[m_id_q, "_quarantine_reason"] = \
        quarantine.loc[m_id_q, "_quarantine_reason"].apply(lambda s: _add_cause(s, "id_respuesta_vacio"))

    # --- CLEAN final ---
    clean = df.loc[~quarantine_mask].copy()
    clean["satisfaccion"] = clean["satisfaccion_num"].astype("Int64")
    clean.drop(columns=[c for c in ["_satisfaccion_norm", "satisfaccion_num"] if c in clean.columns],
               inplace=True)

    for col in ["canal", "producto", "tienda", "agente"]:
        if col in clean.columns:
            clean[col] = clean[col].apply(_norm_text)

    return clean, quarantine
