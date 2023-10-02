import hashlib

import geopandas as gpd
import pandas as pd

SHIFT_START_TIMES = {
    "A": pd.DateOffset(hours=6, minutes=15),
    "B": pd.DateOffset(hours=9, minutes=15),
    "C": pd.DateOffset(hours=16, minutes=45),
    "D": pd.DateOffset(hours=19, minutes=45),
}


def get_shift_start(row):
    return row["date"] + SHIFT_START_TIMES[row["shift"]]


def get_shift_end(row):
    return get_shift_start(row) + pd.DateOffset(hours=11, minutes=15)


# Using the coordinate ref system that is appropriate for NJ
def convert_crs(geo_df):
    return geo_df.to_crs(epsg=3424)  # https://epsg.io/3424


def convert_points_to_boxes(predictions):
    assert predictions["geometry"].iloc[0].geom_type == "Point"
    return predictions.assign(
        geometry=lambda df: df["geometry"].buffer(
            600 / 2, cap_style=3
        )  # A 600-by-600 square
    )


def add_pred_id(df):
    return df.assign(
        pred_id=lambda df: (
            df[
                [
                    "report_id",
                    "title",
                    "date",
                    "label",
                    "shift",
                    "incident_types",
                    "lat",
                    "lon",
                ]
            ]
            .astype(str)
            .apply("|".join, axis=1)
            .apply(lambda x: hashlib.sha1(x.encode("utf-8")).hexdigest()[:8])
        )
    )


def match_dosage_to_preds(dosage_file, pred_file):
    predictions_raw = pd.read_csv(
        pred_file,
        parse_dates=["date"],
    ).pipe(add_pred_id)

    predictions = (
        predictions_raw.drop(columns=["report_id", "department", "geoid"])
        .assign(
            shift=lambda df: df["shift"].str.extract(r"([A-D])"),
            pred_shift_start=lambda df: df.apply(get_shift_start, axis=1),
            pred_shift_end=lambda df: df.apply(get_shift_end, axis=1),
        )
        .pipe(
            lambda df: gpd.GeoDataFrame(
                df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326"
            )
        )
        .pipe(convert_crs)
    )

    dosage_raw = pd.read_csv(dosage_file, parse_dates=["Started", "Ended"])
    dosage = (
        dosage_raw.loc[lambda df: df["Started"].notnull()]
        .drop(columns=["Time Spent"])
        .rename(
            columns={
                "Latitude": "lat",
                "Longitude": "lng",
                "Started": "dosage_start",
                "Ended": "dosage_end",
                "Location": "address",
                "Inc #": "inc_id",
                "Inc Type": "inc_type",
                "Unit ID": "unit_id",
            }
        )
        .drop_duplicates(["inc_id", "address", "dosage_start", "dosage_end"])
        .astype({"inc_id": int})
        .pipe(
            lambda df: gpd.GeoDataFrame(
                df, geometry=gpd.points_from_xy(df["lng"], df["lat"]), crs="EPSG:4326"
            )
        )
        .pipe(convert_crs)
    )

    assert dosage["inc_id"].value_counts().max() == 1

    predictions_with_dosage = (
        predictions[
            [
                "pred_id",
                "geometry",
                "pred_shift_start",
                "pred_shift_end",
            ]
        ]
        .pipe(convert_points_to_boxes)
        .sjoin(
            (
                dosage[
                    [
                        "inc_id",
                        "geometry",
                        "dosage_start",
                        "dosage_end",
                    ]
                ]
            ),
            how="left",
            predicate="intersects",
        )
        .loc[
            lambda df: (
                # Dosage start is inside the prediction shift
                (
                    (df["dosage_start"] >= df["pred_shift_start"])
                    & (df["dosage_start"] <= df["pred_shift_end"])
                )
                |
                # ... or dosage end is inside the prediction shift
                (
                    (df["dosage_end"] >= df["pred_shift_start"])
                    & (df["dosage_end"] <= df["pred_shift_end"])
                )
                |
                # ... or dosage extrends from before the dosage shift to after it
                (
                    (df["dosage_start"] <= df["pred_shift_start"])
                    & (df["dosage_end"] >= df["pred_shift_end"])
                )
            )
        ]
        .drop(columns=["index_right"])
    )

    pred_out = predictions.assign(
        has_dosage_during_pred=lambda df: df["pred_id"].isin(
            predictions_with_dosage["pred_id"]
        )
    )

    cols = [
        "date",
        "pred_id",
        "title",
        "lat",
        "lon",
        "address",
        "shift",
        "incident_types",
        "pred_shift_start",
        "pred_shift_end",
        "has_dosage_during_pred",
    ]

    return pred_out[cols]


def main():
    df = match_dosage_to_preds(
        "data/inputs/plainfield_dosage.csv",
        "data/inputs/plainfield_predictions_with_shifts.csv",
    )
    df.to_csv("data/processed/predictions_with_dosage.csv", index=False)


if __name__ == "__main__":
    main()
