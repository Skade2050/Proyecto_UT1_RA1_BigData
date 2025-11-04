# run.py
from project.ingest import read_excels
from project.clean import clean_data
from project.store import save_to_sqlite, save_table_sqlite, save_parquet
from project.report import generate_report, export_quality_report

if __name__ == "__main__":
    # 1) RAW
    df_raw = read_excels("data/drops")
    save_to_sqlite(df_raw, table="raw_encuestas")

    # 2) CLEAN
    df_clean, df_quarantine = clean_data(df_raw)
    save_table_sqlite(df_clean, table="clean_encuestas")
    save_table_sqlite(df_quarantine, table="quarantine_encuestas")

    # 3) Parquet limpio + Reporte + Informe de calidad (extra)
    save_parquet(df_clean, "project/output/clean_encuestas.parquet")
    generate_report(df_clean, df_quarantine, "project/output/reporte.md")
    export_quality_report(df_clean, df_quarantine, "project/output/informe_de_calidad.xlsx")

    print("Pipeline RAW→CLEAN + Reporte generado ✅")
