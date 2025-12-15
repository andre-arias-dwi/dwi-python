import pandas as pd
from pathlib import Path

INPUT_CSV = Path("data/fox_utm_tracker.csv")
LOOKUP_OUT = Path("data/fox_gls_lookup.csv")
WHERE_OUT = Path("fox_gls_where_clause.sql")

def main():
    df = pd.read_csv(INPUT_CSV)

    # Rename columns to something clean once
    df = df.rename(columns={
        "utm_source*": "utm_source",
        "utm_medium*": "utm_medium",
        "utm_campaign*": "utm_campaign",
        "Marketing Channel": "marketing_channel"
    })

    # 1) Unique source / medium combos
    pairs = (
        df[["utm_source", "utm_medium"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["utm_source", "utm_medium"])
    )

    print("Unique utm_source / utm_medium pairs:")
    print(pairs)

    # 2) Generate lookup for BigQuery
    lookup = (
        df[["utm_source", "utm_medium"]]
        .drop_duplicates()
        .sort_values(["utm_source", "utm_medium"])
    )
    LOOKUP_OUT.parent.mkdir(parents=True, exist_ok=True)
    lookup.to_csv(LOOKUP_OUT, index=False)
    print(f"\nLookup CSV written to: {LOOKUP_OUT}")

    # 3) Generate a WHERE clause using STRUCT(source, medium) IN (...)
    struct_list = [
        f"  STRUCT('{row.utm_source}', '{row.utm_medium}')"
        for _, row in pairs.iterrows()
    ]
    where_clause = (
        "AND STRUCT(traffic_source.source, traffic_source.medium) IN (\n"
        + ",\n".join(struct_list)
        + "\n)"
    )

    WHERE_OUT.write_text(where_clause, encoding="utf-8")
    print(f"\nWHERE clause written to: {WHERE_OUT}")

if __name__ == "__main__":
    main()
