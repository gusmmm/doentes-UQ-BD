from fastapi import APIRouter, HTTPException, Body

from ..models.patient import PatientData, PatientUpdateData
from ..config.db import conn
from ..schemas.patient import patientDataEntity, patientDataListEntity

patient = APIRouter()

@patient.get('/')
async def find_all_patients():
    return patientDataListEntity(conn.local.patient.find())

@patient.put('/{id_patient}')
async def update_patient(id_patient: int, update_data: PatientUpdateData):
    # Convert the update data to dict and remove None values
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid update data provided")

    # Find and update the patient
    result = conn.local.patient.update_one(
        {"_id": id_patient},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Patient with id_patient {id_patient} not found")

    # Return the updated patient
    updated_patient = conn.local.patient.find_one({"_id": id_patient})
    if updated_patient:
        return patientDataEntity(updated_patient)
    
    raise HTTPException(status_code=404, detail="Patient not found after update")

@patient.delete('/{id_patient}')
async def delete_patient(id_patient: int):
    result = conn.local.patient.delete_one({"_id": id_patient})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Patient with id_patient {id_patient} not found")
        
    return {"message": f"Patient with id_patient {id_patient} successfully deleted"}

@patient.post('/')
async def create_patient(
    patient: PatientData = Body(
        ...,
        description="Patient data including required id_patient which will be used as the unique identifier",
        example={
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
    )
):
    # Convert patient to dict, set _id, and remove id_patient
    patient_dict = dict(patient)
    patient_dict['_id'] = patient_dict.pop('id_patient')
    
    try:
        conn.local.patient.insert_one(patient_dict)
    except Exception as e:
        if 'duplicate key error' in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Patient with id_patient {patient.id_patient} already exists"
            )
        raise e
    
    return patientDataEntity(conn.local.patient.find_one({"_id": patient.id_patient}))
