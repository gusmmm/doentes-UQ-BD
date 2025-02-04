from pathlib import Path
from typing import Optional
from datetime import datetime

from .patient_extractor import PatientDataExtractor, PatientData
from .burn_extractor import BurnDataExtractor, BurnData
from .medical_history_extractor import MedicalHistoryExtractor, MedicalHistory

def format_date(date_str: Optional[str]) -> Optional[str]:
    """Convert date string to YYYY-MM-DD format."""
    if not date_str:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None

def create_mongo_document(patient_data: PatientData, burn_data: BurnData, medical_history: MedicalHistory) -> dict:
    """Create a MongoDB document from patient and burn data."""
    
    # Create base document structure
    doc = {
        "_id": patient_data.id_patient,
        "name": patient_data.full_name,
        "gender": patient_data.gender,
        "dob": format_date(patient_data.date_of_birth),
        "address": patient_data.address,
        "contact": {
            "phone": "",  # Not currently extracted
            "email": ""  # Not currently extracted
        },
        "ids": {
            "patient_id": str(patient_data.process_number) if patient_data.process_number else "",
            "sns_number": ""  # Not currently extracted
        }
    }
    
    # Add burn-specific data
    if burn_data:
        doc.update({
            "injury_date": format_date(burn_data.injury_date),
            "injury_time": burn_data.injury_time,
            "injury_cause": burn_data.injury_cause,
            "injury_location": burn_data.injury_location,
            "burn_degree": [
                {
                    "location": burn.location,
                    "degree": burn.degree.value,
                    "laterality": burn.laterality
                }
                for burn in burn_data.burn_degree
            ],
            "tbsa": burn_data.tbsa,
            "inhalation_injury": burn_data.inhalation_injury,
            "pre_hospital_intubation": burn_data.pre_hospital_intubation,
            "pre_hospital_fluid": [
                {
                    "type": fluid.type,
                    "volume": fluid.volume
                }
                for fluid in burn_data.pre_hospital_fluid
            ],
            "pre_hospital_other": burn_data.pre_hospital_other,
            "admission_date": format_date(patient_data.admission_date),
            "admission_time": patient_data.admission_time,
            "mechanical_ventilation": burn_data.mechanical_ventilation,
            "parkland_formula": burn_data.parkland_formula,
            "consultations": burn_data.consultations,
            "interventions": [
                {
                    "date": format_date(intervention.date),
                    "procedure": intervention.procedure,
                    "details": intervention.details
                }
                for intervention in burn_data.interventions
            ]
        })
    
    # Add discharge information
    doc.update({
        "discharge_date": format_date(patient_data.discharge_date),
        "discharge_time": patient_data.discharge_time,
        "discharge_destination": patient_data.destination,
        "death_date": None,  # Not currently extracted
        "cause_of_death": None,  # Not currently extracted
        "autopsy": False  # Not currently extracted
    })
    
    # Add medical history section
    doc.update({
        "medical_history": {
            "diseases": medical_history.diseases if medical_history else [],
            "medications": medical_history.medications if medical_history else [],
            "previous_surgeries": [
                {
                    "procedure": surgery.procedure,
                    "date": format_date(surgery.date) if surgery.date else None,
                    "details": surgery.details
                }
                for surgery in (medical_history.previous_surgeries if medical_history else [])
            ],
            "allergies": medical_history.allergies if medical_history else []
        }
    })
    
    return doc

def extract_and_format_data(filename: str | Path, project_root: Path) -> Optional[dict]:
    """Extract data from markdown file and format it for MongoDB."""
    try:
        # Extract patient data
        patient_extractor = PatientDataExtractor(project_root)
        patient_data = patient_extractor.extract(filename)
        if not patient_data:
            print("Failed to extract patient data")
            return None
            
        # Extract burn data
        burn_extractor = BurnDataExtractor(project_root)
        burn_data = burn_extractor.extract(filename)
        if not burn_data:
            print("Failed to extract burn data")
            return None
            
        # Extract medical history
        medical_extractor = MedicalHistoryExtractor(project_root)
        medical_history = medical_extractor.extract(filename)
        if not medical_history:
            print("Warning: No medical history extracted")
            
        # Create MongoDB document
        mongo_doc = create_mongo_document(patient_data, burn_data, medical_history)
        return mongo_doc
        
    except Exception as e:
        print(f"Error in data extraction and formatting: {str(e)}")
        return None
