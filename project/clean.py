# project/clean.py
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

def clean_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df_raw.copy()

    # --- normaliza nombres y trim en todas las columnas texto ---
    df.columns = [str(c).strip().lower() for c in df.columns]
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # --- fecha ---
    df["fecha"] = pd.to_datetime(df.get("fecha"), errors="coerce")

    # --- satisfaccion ---
    # 1) mapa NS/NC -> NaN
    if "satisfaccion" in df.columns:
        df["_satisfaccion_norm"] = df["satisfaccion"].apply(_norm_text)
        df.loc[df["_satisfaccion_norm"].isin(NSNC_VALUES), "satisfaccion"] = pd.NA

        # 2) intenta convertir números
        df["satisfaccion_num"] = pd.to_numeric(df["satisfaccion"], errors="coerce").astype("Int64")

        # 3) filas fuera de rango -> quarantine
        bad_range = ~(df["satisfaccion_num"].between(1, 10)) & df["satisfaccion_num"].notna()
    else:
        df["satisfaccion_num"] = pd.Series([pd.NA] * len(df), dtype="Int64")
        bad_range = pd.Series([False] * len(df))

    # --- dedupe (si llega duplicado el id_respuesta, gana el último por _ingest_ts) ---
    key_cols = [c for c in ["id_respuesta"] if c in df.columns]
    if key_cols:
        df = df.sort_values(df.columns.intersection(["_ingest_ts"]).tolist()).drop_duplicates(
            subset=key_cols, keep="last"
        )

    # --- reglas de quarantine ---
    quarantine_mask = (
        df["fecha"].isna() |               # fecha inválida
        bad_range                           # satisfaccion fuera de 1-10
    )

    quarantine = df.loc[quarantine_mask].copy()
    quarantine["_quarantine_reason"] = None
    quarantine.loc[quarantine["fecha"].isna(), "_quarantine_reason"] = \
        (quarantine["_quarantine_reason"].fillna("") + "fecha_invalida;").str.strip(";")
    quarantine.loc[bad_range.reindex(df.index, fill_value=False), "_quarantine_reason"] = \
        (quarantine["_quarantine_reason"].fillna("") + "satisf_fuera_rango;").str.strip(";")

    # --- CLEAN: castea tipos finales ---
    clean = df.loc[~quarantine_mask].copy()
    # satisfaccion final (Int64 con NaN permitido)
    clean["satisfaccion"] = clean["satisfaccion_num"].astype("Int64")
    clean.drop(columns=[c for c in ["_satisfaccion_norm", "satisfaccion_num"] if c in clean.columns],
               inplace=True)

    # valores texto normalizados opcionales
    for col in ["canal", "producto", "tienda", "agente"]:
        if col in clean.columns:
            clean[col] = clean[col].apply(_norm_text)

    return clean, quarantine
