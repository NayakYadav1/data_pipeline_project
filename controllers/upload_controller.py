from fastapi import APIRouter, UploadFile, File
from services.parser_utils import detect_and_parse
from services.preprocessor import preprocess
from models.db_model import insert_cleaned_data

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        df = detect_and_parse(file.file, file.filename)
        cleaned_df, warnings = preprocess(df)
        insert_cleaned_data("cleaned_data", cleaned_df, file.filename.split('.')[-1])
        preview = cleaned_df.head(20).to_dict(orient="records")
        return {
            "preview": preview,
            "warnings": warnings,
            "message": "File processed and saved successfully."
        }
    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}