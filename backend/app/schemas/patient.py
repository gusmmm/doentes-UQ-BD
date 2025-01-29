def patientDataEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "id_patient": item["id_patient"],
        "gender": item["gender"],
        "date_of_birth": item["date_of_birth"],
        "process_number": item["process_number"],
        "full_name": item["full_name"],
        "location": item["location"],
        "date_of_admission_UQ": item["date_of_admission_UQ"],
        "origin": item["origin"],
        "date_of_discharge": item["date_of_discharge"],
        "destination": item["destination"]
    }

def patientDataListEntity(entity) -> list:
    return [patientDataEntity(item) for item in entity]