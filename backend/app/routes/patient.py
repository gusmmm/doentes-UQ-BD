from fastapi import APIRouter

from ..models.patient import PatientData
from ..config.db import conn
from ..schemas.patient import patientDataEntity, patientDataListEntity

patient = APIRouter()

@patient.get('/')
async def find_all_patients():
    print(conn.local.patient.find())
    print(patientDataListEntity(conn.local.patient.find()))
    return patientDataListEntity(conn.local.patient.find())  # conn.patients is the collection

@patient.post('/')
async def create_patient(patient: PatientData):
    conn.local.patient.insert_one(dict(patient))
    return patientDataEntity(conn.local.patient.find_one({"id_patient": patient.id_patient}))