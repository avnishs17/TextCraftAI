from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from fastapi.templating import Jinja2Templates
from textCraftAI.pipeline.enhanced_prediction import EnhancedPredictionPipeline
from pydantic import BaseModel
from typing import Optional

# Request models
class TextRequest(BaseModel):
    text: str

class ParaphraseRequest(BaseModel):
    text: str
    length_factor: float = 1.0  # Default to same length as input

app = FastAPI(
    title="TextCraftAI",
    description="AI-powered text processing service with summarization, paraphrasing, and file processing capabilities",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "TextCraftAI",
        "version": "2.0.0",
        "features": [
            "dialogue_summarization", 
            "text_paraphrasing", 
            "file_processing", 
            "pdf_upload", 
            "docx_upload", 
            "text_cleaning", 
            "api_endpoints"
        ]
    }

# Main web interface (only summarization)
@app.get("/", tags=["web"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Prediction API endpoint
@app.post("/predict", tags=["api"])
async def predict_route(request: TextRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 10,000 characters allowed.")
        
        obj = EnhancedPredictionPipeline()
        summary = obj.summarize_text(request.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Paraphrasing API endpoint
@app.post("/paraphrase", tags=["api"])
async def paraphrase_route(request: ParaphraseRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 10,000 characters allowed.")
        
        if not (0.3 <= request.length_factor <= 2.0):
            raise HTTPException(status_code=400, detail="Length factor must be between 0.3 and 2.0")
        
        obj = EnhancedPredictionPipeline()
        paraphrased = obj.paraphrase_text(request.text, request.length_factor)
        return {"paraphrased_text": paraphrased, "length_factor": request.length_factor}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paraphrasing failed: {str(e)}")

# File upload and processing endpoint
@app.post("/upload", tags=["api"])
async def upload_file(
    file: UploadFile = File(...),
    operation: str = Form(...),
    length_factor: float = Form(1.0)
):
    try:
        # Validate operation
        if operation not in ["summarize", "paraphrase"]:
            raise HTTPException(status_code=400, detail="Invalid operation. Choose 'summarize' or 'paraphrase'")
        
        # Validate length_factor if paraphrasing
        if operation == "paraphrase" and not (0.3 <= length_factor <= 2.0):
            raise HTTPException(status_code=400, detail="Length factor must be between 0.3 and 2.0")
        
        # Validate file type
        allowed_types = ['.pdf', '.docx', '.txt']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_types):
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF, DOCX, or TXT files only.")
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="File too large. Maximum 5MB allowed.")
        
        # Process file
        obj = EnhancedPredictionPipeline()
        result = obj.process_file(file_content, file.filename, operation, length_factor)
        
        return {
            "filename": file.filename,
            "operation": operation,
            "length_factor": length_factor if operation == "paraphrase" else None,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

# For Railway deployment - use PORT environment variable
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)