from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
from groq import Groq

from app.api import grok
from app.db_config import get_database_connection
from app import models
from app.core.EDA import get_summary

import io
import os
import re
import pandas as pd
import numpy as np
import json

router = APIRouter()


class CleanRequest(BaseModel):
    operations: List[str]


@router.get("/dataset/{dataset_id}/data")
async def columns_and_rows(
    dataset_id: int,
    database: AsyncSession = Depends(get_database_connection)
):
    d1 = await database.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )

    dataset = d1.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = pd.read_csv(io.StringIO(dataset.content))

    fivegrid = df.iloc[:20, :5].replace({np.nan: None})
    response = {
        "columns": fivegrid.columns.tolist(),
        "rows": fivegrid.values.tolist()
    }
    return response

@router.get("/dataset/{dataset_id}/suggestions")
async def suggestions(
    dataset_id: int,
    database: AsyncSession = Depends(get_database_connection)
):
    result = await database.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )
    dataset = result.scalars().first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    summary, dataset = await get_summary(dataset)

    client = Groq(api_key=os.getenv("GROK_API_KEY"))

    prompt = (
        f"Here is a summary of a dataset:\n{summary}\n\n"
        "Suggest practical data cleaning steps for this dataset.\n"
        "Return ONLY a JSON array, nothing else, in this exact format:\n"
        '[{"suggested_change": "your suggestion here"}]'
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            raise HTTPException(status_code=429, detail="AI rate limit reached. Please wait a few minutes and try again.")
        raise HTTPException(status_code=503, detail=f"AI service error: {error_str}")

    try:
        cleaned = re.sub(r"```(?:json)?|```", "", answer).strip()
        suggestions_json = json.loads(cleaned)
    except json.JSONDecodeError:
        suggestions_json = [{"suggested_change": "Error parsing model response"}]

    return {"suggestions": suggestions_json}


@router.post("/dataset/{dataset_id}/clean")
async def clean_dataset(
    dataset_id: int,
    body: CleanRequest,
    database: AsyncSession = Depends(get_database_connection)
):
    result = await database.execute(
        select(models.Dataset).where(models.Dataset.id == dataset_id)
    )
    dataset = result.scalars().first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(io.StringIO(dataset.content))

    if "item1" in body.operations:
        for col in df.columns:

            # Skip columns that are already a proper numeric or datetime type
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            col_lower = col.lower()
            sample = df[col].dropna().astype(str)

            # If the column name contains date/time words, try converting it to datetime
            date_keywords = ["date", "time", "year", "month", "day", "created", "updated", "timestamp", "born", "founded"]
            looks_like_date_column = any(word in col_lower for word in date_keywords)

            if looks_like_date_column:
                converted = pd.to_datetime(df[col], errors='coerce')
                # Only apply if at least half the values converted successfully
                if converted.notna().mean() >= 0.5:
                    df[col] = converted
                    continue

            # Check if the values look like booleans (yes/no, true/false, 1/0)
            bool_map = {"true": True, "false": False, "yes": True, "no": False, "1": True, "0": False}
            unique_vals = sample.str.lower().unique()
            looks_like_bool = all(v in bool_map for v in unique_vals)

            if looks_like_bool and len(unique_vals) <= 2:
                # Convert the column to actual True/False boolean values
                df[col] = sample.str.lower().map(bool_map)
                continue

            # Check if the values are mostly numeric (strip spaces, dots, dashes)
            def looks_numeric(val):
                cleaned = str(val).strip().replace(',', '').replace(' ', '')
                try:
                    float(cleaned)
                    return True
                except ValueError:
                    return False

            numeric_ratio = sample.apply(looks_numeric).mean()

            if numeric_ratio >= 0.7:
                # Convert to numeric, turning anything that fails into NaN
                converted = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')
                df[col] = converted
                continue

            # Check if it looks like a percentage column (e.g. "45%")
            percent_ratio = sample.str.strip().str.endswith('%').mean()

            if percent_ratio >= 0.7:
                # Strip the % sign and convert to a float between 0 and 100
                df[col] = pd.to_numeric(sample.str.replace('%', '').str.strip(), errors='coerce')
                continue

            # Check if it looks like a currency column (e.g. "$1,200.00")
            currency_ratio = sample.str.strip().str.match(r'^[\$\€\£\¥]?[\d,]+\.?\d*$').mean()

            if currency_ratio >= 0.7:
                # Strip currency symbols and commas, then convert to float
                df[col] = pd.to_numeric(
                    sample.str.replace(r'[\$\€\£\¥,]', '', regex=True).str.strip(),
                    errors='coerce'
                )
                continue

            # If nothing matched, it's a plain text column — just clean up extra whitespace
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()

    if "item2" in body.operations:
        # Remove rows that are completely identical across all columns
        df = df.drop_duplicates()

    if "item3" in body.operations:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Fill missing numbers with 0
                df[col] = df[col].fillna(0)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                # Leave missing dates as NaT — filling with 0 would break them
                pass
            else:
                # Fill missing text values with the string "Unknown"
                df[col] = df[col].fillna("Unknown")

    ai_ops = [op for op in body.operations if op not in ("item1", "item2", "item3")]

    if ai_ops:
        prompt = (
            f"You have a pandas DataFrame named 'df' with these columns: {df.columns.tolist()}\n"
            "Apply these cleaning operations:\n"
            + "\n".join(f"- {op}" for op in ai_ops) +
            "\nReturn ONLY executable Python code that modifies 'df'. No imports, no explanations, no markdown."
        )

        code = await grok.ask_grok("", prompt)

        if code.startswith("Error:"):
            raise HTTPException(status_code=503, detail=code)

        code = re.sub(r"```(?:python)?|```", "", code).strip()

        try:
            local_vars = {"df": df, "pd": pd, "np": np}
            exec(code, local_vars)
            df = local_vars["df"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error applying AI suggestions: {str(e)}")

    dataset.content = df.to_csv(index=False)
    await database.commit()

    return {"message": "Dataset cleaned successfully"}