import fitz
import psycopg2
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from paddleocr import PaddleOCR
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import re
import os
import asyncio
import utils.utils as utils
from dotenv import load_dotenv

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection parameters
# Use "db" if FastAPI is running in the same Docker network
load_dotenv()
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

loop = None
@app.on_event("startup")
def startup_event():
    global loop
    loop = asyncio.get_event_loop()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("WebSocket connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("WebSocket disconnected")

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
    async def send_stream_message(self, message: str, message_type: str = "info"):
        for connection in self.active_connections:
            await connection.send_json({"type": message_type, "content": message})
    
    async def send_status_update(self, file_id: int, status: str):
        message = {
            "file_id": file_id,
            "status": status
        }
        for connection in self.active_connections:
            await connection.send_json(message)            

def process_file(file_id: int, temp_file_path: str):
    """Synchronous background task to process the uploaded file."""
    try:
        # Update status to "Parsing"
        asyncio.run_coroutine_threadsafe(manager.send_status_update(file_id, "Parsing"), loop)

        # Extract text from the PDF
        extracted_text = utils.extract_text_from_pdf(temp_file_path)

        # Update status to "Uploading"
        asyncio.run_coroutine_threadsafe(manager.send_status_update(file_id, "Uploading"), loop)

        # Store extracted text and update status to "Completed"
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        update_query = """
        UPDATE file_data
        SET text_content = %s, status = %s
        WHERE id = %s;
        """
        cursor.execute(
            update_query,
            (extracted_text, "Completed", file_id),
        )
        conn.commit()
        conn.close()

        # Update status to "Completed"
        asyncio.run_coroutine_threadsafe(manager.send_status_update(file_id, "Completed"), loop)

    except Exception as e:
        # Update status to "Failed"
        asyncio.run_coroutine_threadsafe(manager.send_status_update(file_id, "Failed"), loop)
        print(f"Error processing file_id {file_id}: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


manager = ConnectionManager()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload a PDF file, extract its text, and store it in the database."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File type must be PDF")

    # Save the uploaded PDF temporarily
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        # Insert a new record with status "Uploading" to get the file_id
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO file_data (file_name, file_type, status)
        VALUES (%s, %s, %s)
        RETURNING id, uploaded_at;
        """
        cursor.execute(
            insert_query,
            (file.filename, "PDF", "Uploading"),
        )
        result = cursor.fetchone()
        file_id = result[0]
        uploaded_at = result[1]
        conn.commit()
        conn.close()

        background_tasks.add_task(process_file, file_id, temp_file_path)

        return {"file_id": file_id, "uploaded_at": uploaded_at, "message": "File is being processed."}

    except Exception as e:
        # await manager.send_status_update(file_id=file_id, status="Failed")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=List[dict])
def list_files():
    """List all uploaded files with metadata."""
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, file_name, uploaded_at, file_type, status FROM file_data"
        )
        rows = cursor.fetchall()
        conn.close()
        target_timezone = ZoneInfo("Asia/Shanghai")
        # Format as a list of dictionaries
        files = [
            {
                "id": row[0],
                "file_name": row[1],
                "uploaded_at": utils.adjust_timezone(row[2], target_timezone),
                "file_type": row[3],
                "status": row[4],
            }
            for row in rows
        ]
        return files

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preview/{file_id}")
def preview_file(file_id: int):
    """Preview the extracted text content of a specific file."""
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT text_content FROM file_data WHERE id = %s", (file_id,))
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            text_content = row[0].replace("\x00", "")
            return {"file_id": file_id, "text_content": row[0]}
        else:
            raise HTTPException(status_code=404, detail="File not found or no text content available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete/{file_id}")
def delete_file(file_id: int):
    try:
      conn = psycopg2.connect(**db_params)
      cursor = conn.cursor()

      cursor.execute("SELECT id FROM file_data WHERE id = %s", (file_id,))
      file_exists = cursor.fetchone()
      
      if not file_exists:
          conn.close()
          raise HTTPException(status_code=404, detail="File not found")
      
      delete_query = "DELETE FROM file_data WHERE id = %s"
      cursor.execute(delete_query, (file_id,))
      conn.commit()
      conn.close()
      print(f"File with ID {file_id} successfully deleted.")
      return {"message": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    # uvicorn main:app --reload
    webbrowser.open("http://127.0.0.1:8000/docs")
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)