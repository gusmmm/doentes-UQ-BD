from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientUpdateData(BaseModel):
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    process_number: Optional[int] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    date_of_admission_UQ: Optional[str] = None 
    origin: Optional[str] = None
    date_of_discharge: Optional[str] = None
    destination: Optional[str] = None

class PatientData(BaseModel):
    id_patient: int = Field(
        ...,
        title="Patient ID",
        description="Required. A unique identifier for the patient that will be used as the primary key.",
        examples=[2301, 2302, 2303]
    )
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    process_number: Optional[int] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    date_of_admission_UQ: Optional[str] = None 
    origin: Optional[str] = None
    date_of_discharge: Optional[str] = None
    destination: Optional[str] = None
    
    class Config:
        collection = "patients"
        json_schema_extra = {
            "example": {
                "id_patient": 2301,
                "gender": "M",
                "date_of_birth": "01-01-1970",
                "process_number": 12345,
                "full_name": "John Doe",
                "location": "Porto",
                "date_of_admission_UQ": "01-01-2023",
                "origin": "Hospital São João",
                "date_of_discharge": "15-01-2023",
                "destination": "Home"
            }
        }
