from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_config import get_database_connection
from app import models

import io
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/dataset/{dataset_id}/visualize")
async def get_visualize(
    dataset_id: int,
    db: AsyncSession = Depends(get_database_connection)
):
    d1 = await db.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )

    dataset = d1.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        dataframe = pd.read_csv(io.StringIO(dataset.content))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not parse dataset: " + str(e))

    preview_columns = dataframe.columns.tolist()[:5]
    preview_df = dataframe[preview_columns].iloc[:15].replace({np.nan: None})
    preview = {
        "columns": preview_columns,
        "rows": preview_df.values.tolist()
    }

    charts = []

    for column_name in dataframe.columns:
        column_data = dataframe[column_name]

        if pd.api.types.is_numeric_dtype(column_data):
            clean_values = column_data.dropna()

            if len(clean_values) == 0:
                continue

            histogram_values, bin_edges = np.histogram(clean_values, bins=10)

            labels = []
            for i in range(len(bin_edges) - 1):
                left = round(bin_edges[i], 2)
                right = round(bin_edges[i + 1], 2)
                labels.append(str(left) + "-" + str(right))

            data_values = []
            for value in histogram_values:
                if pd.isna(value) or np.isinf(value):
                    data_values.append(None)
                else:
                    data_values.append(int(value))

            charts.append({
                "type": "bar",
                "title": "Histogram of " + column_name,
                "labels": labels,
                "data": data_values
            })

        else:
            value_counts = column_data.value_counts().head(10)

            if len(value_counts) == 0:
                continue

            labels = value_counts.index.astype(str).tolist()
            raw_values = value_counts.values.tolist()

            clean_values = []
            for value in raw_values:
                if pd.isna(value) or np.isinf(value):
                    clean_values.append(None)
                else:
                    clean_values.append(int(value))

            charts.append({
                "type": "bar",
                "title": "Top categories in " + column_name,
                "labels": labels,
                "data": clean_values
            })

    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_columns) >= 2:
        for i in range(len(numeric_columns)):
            for j in range(i + 1, len(numeric_columns)):
                col_x = numeric_columns[i]
                col_y = numeric_columns[j]

                pair_dataframe = dataframe[[col_x, col_y]].dropna()

                if len(pair_dataframe) > 100:
                    pair_dataframe = pair_dataframe.sample(n=100, random_state=42)

                scatter_points = []
                for _, row in pair_dataframe.iterrows():
                    x_value = row[col_x]
                    y_value = row[col_y]

                    if pd.isna(x_value) or np.isinf(x_value):
                        x_value = None
                    else:
                        x_value = float(x_value)

                    if pd.isna(y_value) or np.isinf(y_value):
                        y_value = None
                    else:
                        y_value = float(y_value)

                    scatter_points.append({"x": x_value, "y": y_value})

                charts.append({
                    "type": "scatter",
                    "title": "Scatter: " + col_x + " vs " + col_y,
                    "labels": [],
                    "data": scatter_points
                })

    if len(numeric_columns) >= 2:
        correlation_matrix = dataframe[numeric_columns].corr()

        matrix_data = []
        for row_index in range(len(correlation_matrix.columns)):
            column_name = correlation_matrix.columns[row_index]
            row_values = correlation_matrix.iloc[row_index].values.tolist()

            clean_row = []
            for value in row_values:
                if pd.isna(value) or np.isinf(value):
                    clean_row.append(None)
                else:
                    clean_row.append(round(float(value), 3))

            matrix_data.append({
                "name": column_name,
                "data": clean_row
            })

        charts.append({
            "type": "matrix",
            "title": "Correlation Matrix",
            "labels": correlation_matrix.columns.tolist(),
            "data": matrix_data
        })

    return {
        "preview": preview,
        "charts": charts
    }


@router.get("/dataset/{dataset_id}/download")
async def download_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_database_connection)
):
    d1 = await db.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )

    dataset = d1.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    from fastapi.responses import Response
    return Response(
        content=dataset.content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cleaned_dataset.csv"}
    )