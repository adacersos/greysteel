# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
import shutil
import os
import sys

# Temporary path for pipeline
sys.path.append(r'/Users/adamc/Documents/greysteel/PSA_app/extractor')
from pipeline import run_psa_extractor

# Initialize FastAPI app
app = FastAPI(title="PSA Extraction API")

# Upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Simple test UI ---
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>PSA Extraction Test</title>
        </head>
        <body>
            <h1>Upload a PSA PDF</h1>
            <form action="/extract" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept="application/pdf">
                <input type="submit" value="Upload & Extract">
            </form>
        </body>
    </html>
    """

# --- API Endpoint ---
@app.post("/extract")
async def extract_psa(file: UploadFile = File(...)):
    """
    Upload a PDF PSA and extract milestones using Gemini pipeline.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call your pipeline
    try:
        extracted_data = run_psa_extractor(file_path)
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

    # Return extracted results
    return JSONResponse(
        content={
            "status": "success",
            "file": file.filename,
            "data": extracted_data
        }
    )

# --- Run Server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)