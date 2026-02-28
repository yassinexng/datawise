from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import grok
from app.db_config import get_database_connection
from app import models

import io
import pandas as pd
import numpy as np

router = APIRouter()


def detect_outliers(dataframe, column):
    Q1 = dataframe[column].quantile(0.25)
    Q3 = dataframe[column].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - (1.5 * IQR)
    upper_bound = Q3 + (1.5 * IQR)

    outlier_rows = dataframe[
        (dataframe[column] < lower_bound) |
        (dataframe[column] > upper_bound)
    ]

    outlier_count = len(outlier_rows)
    return outlier_count

async def get_summary(dataset_model):
    try:
        csv_text = dataset_model.content
        string_buffer = io.StringIO(csv_text)
        dataframe = pd.read_csv(string_buffer)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Could not parse dataset: " + str(e)
        )

    dataset_head = dataframe.head().to_string()
    dataset_shape = str(dataframe.shape)
    dataset_stats = dataframe.describe(include="all").to_string()
    missing_values = dataframe.isnull().sum().to_string()
    column_types = dataframe.dtypes.to_string()

    summary = (
        "Dataset head:\n"
        + dataset_head
        + "\n\nShape:\n"
        + dataset_shape
        + "\n\nStats:\n"
        + dataset_stats
        + "\n\nMissing:\n"
        + missing_values
        + "\n\nTypes:\n"
        + column_types
    )
    return summary, dataframe

@router.get("/dataset/{dataset_id}/analyze")
async def get_analysis(
    dataset_id: int,
    db: AsyncSession = Depends(get_database_connection)
):
    d1 = await db.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )

    dataset = d1.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    summary, dataframe = await get_summary(dataset)


    initial = (
    "Return ONLY a JSON array. "
    "Use AT MOST these keys: "
    "Statistics, Missing Values, Data Types. "
    "For Statistics: include ONLY count, mean, min, max. "
    "Do not include explanations. "
    "Do not nest deeper than column -> metric -> value."
)

    initial_eda = await grok.ask_grok(summary, initial)

    charts = []

    # Univariate: bar charts for categorical, hist for numeric
    for column_name in dataframe.columns:

        column_data = dataframe[column_name]

        if pd.api.types.is_numeric_dtype(column_data):

            clean_values = column_data.dropna()

            histogram_values, bin_edges = np.histogram(
                clean_values,
                bins=10
            )

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

            chart_object = {
                "type": "bar",
                "title": "Histogram of " + column_name,
                "labels": labels,
                "data": data_values
            }

            charts.append(chart_object)

        else:
            value_counts = column_data.value_counts().head(10)

            labels = value_counts.index.astype(str).tolist()
            raw_values = value_counts.values.tolist()

            clean_values = []
            for value in raw_values:
                if pd.isna(value) or np.isinf(value):
                    clean_values.append(None)
                else:
                    clean_values.append(int(value))

            chart_object = {
                "type": "bar",
                "title": "Top categories in " + column_name,
                "labels": labels,
                "data": clean_values
            }

            charts.append(chart_object)

    # Bivariate: scatter for pairs of numeric columns
    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_columns) >= 2:

        for i in range(len(numeric_columns)):
            for j in range(i + 1, len(numeric_columns)):

                col_x = numeric_columns[i]
                col_y = numeric_columns[j]

                pair_dataframe = dataframe[[col_x, col_y]].dropna()

                if len(pair_dataframe) > 100:
                    pair_dataframe = pair_dataframe.sample(
                        n=100,
                        random_state=42
                    )

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

                    scatter_points.append({
                        "x": x_value,
                        "y": y_value
                    })

                chart_object = {
                    "type": "scatter",
                    "title": "Scatter: " + col_x + " vs " + col_y,
                    "labels": [],
                    "data": scatter_points
                }

                charts.append(chart_object)

    # Correlation heatmap for ApexCharts heatmap
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
                    clean_row.append(float(value))

            matrix_data.append({
                "name": column_name,
                "data": clean_row
            })

        chart_object = {
            "type": "matrix",
            "title": "Correlation matrix",
            "labels": correlation_matrix.columns.tolist(),
            "data": matrix_data
        }

        charts.append(chart_object)

    return {
        "initial_eda": initial_eda,
        "charts_v": charts
    }