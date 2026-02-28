import pymupdf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from io import BytesIO
from app import models
from app.db_config import get_database_connection

router = APIRouter()


def read_pdf(file_bytes):
    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text()
        text += page_text + '\n'
    doc.close()
    doc_text = text.strip()
    return doc_text

def read_excel(file_bytes):
    try:
        file_stream = BytesIO(file_bytes)
        df = pd.read_excel(file_stream)
        text = df.to_csv(index=False)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read Excel file.")

def read_csv(file_bytes):
    try:
        file_stream = BytesIO(file_bytes)
        df = pd.read_csv(file_stream)
        text = df.to_csv(index=False)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read CSV file.")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    username: str = Form(...),
    db: AsyncSession = Depends(get_database_connection)
):
    content = await file.read()

    file_type = file.content_type
    Lfilename = file.filename.lower()
    if Lfilename.endswith('.pdf'):
        text = read_pdf(content)
    elif Lfilename.endswith('.xlsx') or Lfilename.endswith('.xls'):
        text = read_excel(content)
    elif Lfilename.endswith('.csv'):
        text = read_csv(content)
    elif file_type == "text/plain" or Lfilename.endswith('.txt'):
        decoded_text = content.decode("utf-8")
        text = decoded_text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if not text:
        raise HTTPException(status_code=400, detail="File is empty")
    
    filename_parts = file.filename.split('.')
    file_ext = filename_parts[-1][:10]

    dataset = models.Dataset(
        username=username,
        name=file.filename,
        content=text,
        file_size=len(content)
    )
    db.add(dataset)
    await db.commit()
    
    return {
        "id": dataset.id,
        "filename": dataset.name,
        "username": dataset.username,
        "file_size": dataset.file_size,
        "content_preview": text[:500],
        "created_at": dataset.created_at
    }
