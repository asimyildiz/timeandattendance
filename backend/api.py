import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from time_and_attendance import parse_excel
from datetime import time, timedelta
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize(obj: Any) -> Any:
    if isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    elif isinstance(obj, timedelta):
        return obj.total_seconds() / 3600
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    else:
        return obj

@app.post("/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    try:
        # Read file content into memory
        content = await file.read()

        # Pass a BytesIO stream to parse_excel
        from io import BytesIO
        file_stream = BytesIO(content)

        result = parse_excel(file_stream)

        # Return response
        serialized_result = serialize(result)
        
        return JSONResponse(content=serialized_result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        await file.close()            
