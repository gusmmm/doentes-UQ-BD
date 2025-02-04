from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app = FastAPI()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.local

@app.post("/import_patient/{file_name}")
async def import_patient(file_name: str):
    """Import patient data from JSON file to MongoDB."""
    try:
        # Construct file path
        json_path = project_root / "data" / "json" / f"{file_name}.json"
        
        if not json_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File {file_name}.json not found"
            )
            
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            patient_data = json.load(f)
            
        # Check if patient already exists
        existing = db.patient.find_one({"_id": patient_data["_id"]})
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Patient with _id {patient_data['_id']} already exists"
            )
            
        # Insert into MongoDB
        result = db.patient.insert_one(patient_data)
        
        return {
            "message": "Patient imported successfully",
            "_id": patient_data["_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing patient: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)