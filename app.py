from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
import sys
import os
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from fastapi.responses import Response
from textCraftAI.pipeline.prediction import PredictionPipeline
from pydantic import BaseModel

# Request model for prediction
class TextRequest(BaseModel):
    text: str

text:str = "What is Text Summarization?"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount static files (for future use)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Web UI Routes
@app.get("/", tags=["web"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/train-ui", tags=["web"])
async def train_ui(request: Request):
    return templates.TemplateResponse("train.html", {"request": request})


# API Routes (keeping your existing endpoints)
@app.get("/train")
async def training():
    try:
        os.system("python main.py")
        return Response("Training successful !!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")
    

@app.post("/predict")
async def predict_route(request: TextRequest):
    try:
        obj = PredictionPipeline()
        summary = obj.predict(request.text)
        return {"summary": summary}
    except Exception as e:
        raise e
    

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)