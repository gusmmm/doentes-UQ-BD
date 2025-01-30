def patientDataEntity(item) -> dict:
    # Map _id to id_patient and include all other fields except _id
    result = {"id_patient": item["_id"]}
    # Add all other fields except _id
    result.update({k: v for k, v in item.items() if k != '_id'})
    return result

def patientDataListEntity(entity) -> list:
    return [patientDataEntity(item) for item in entity]
