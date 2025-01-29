from fastapi import APIRouter, HTTPException

from ..models.patient import PatientData, PatientUpdateData
from ..config.db import conn
from ..schemas.patient import patientDataEntity, patientDataListEntity

patient = APIRouter()

@patient.get('/')
async def find_all_patients():
    print(conn.local.patient.find())
    print(patientDataListEntity(conn.local.patient.find()))
    return patientDataListEntity(conn.local.patient.find())  # conn.patients is the collection

@patient.put('/{id_patient}')
async def update_patient(id_patient: int, update_data: PatientUpdateData):
    # Convert the update data to dict and remove None values
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid update data provided")

    # Find and update the patient
    result = conn.local.patient.update_one(
        {"id_patient": id_patient},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Patient with id_patient {id_patient} not found")

    # Return the updated patient
    updated_patient = conn.local.patient.find_one({"id_patient": id_patient})
    if updated_patient:
        return patientDataEntity(updated_patient)
    
    raise HTTPException(status_code=404, detail="Patient not found after update")

@patient.delete('/{id_patient}')
async def delete_patient(id_patient: int):
    result = conn.local.patient.delete_one({"id_patient": id_patient})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Patient with id_patient {id_patient} not found")
        
    return {"message": f"Patient with id_patient {id_patient} successfully deleted"}

@patient.post('/')
async def create_patient(patient: PatientData):
    # Check if patient with same id_patient already exists
    existing_patient = conn.local.patient.find_one({"id_patient": patient.id_patient})
    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail=f"Patient with id_patient {patient.id_patient} already exists"
        )
    
    conn.local.patient.insert_one(dict(patient))
    return patientDataEntity(conn.local.patient.find_one({"id_patient": patient.id_patient}))
