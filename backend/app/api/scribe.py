"""
Scribe API Routes

Endpoints for Scribe agent functionality (e.g., file upload).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import docx
import io

router = APIRouter()

@router.post("/upload")
async def upload_requirements(file: UploadFile = File(...)):
    """
    Upload a requirements file (txt, md, docx) and extract text.
    """
    content = await file.read()
    filename = file.filename.lower()

    extracted_text = ""

    try:
        if filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            extracted_text = "\n".join(full_text)

        elif filename.endswith(".txt") or filename.endswith(".md"):
            extracted_text = content.decode("utf-8")

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload .txt, .md, or .docx"
            )

        if not extracted_text.strip():
             raise HTTPException(
                status_code=400,
                detail="File is empty or text could not be extracted"
            )

        return {"filename": file.filename, "text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
