PATIENT DATA EXTRACTION
----------------------
# gender:
    - return M or F.
    - Look for "Masculino" or "Feminino", usually in the first lines of the text.
    - If not found, set to None.


# date_of_birth:
    - in the first lines of the file
    - it is found in the format yyyy-mm-dd. Example: 1965-05-14
    - return in the format dd-mm-yyyy
    - If not found, set to None.


# full_name:
    - full name of the patient
    - in the first lines of the file
    - after the date of birth
    - before the process number
    - If not found, set to None.


# process_number :
    - Número de Processo
    - It's an integer number
    - Found after the patient's name, in the line before "Nº Processo:"
    - If not found, set to None.


# location:
    - it is where the patient lives
    - just mention the city or region
    - usually found after the street name
    - usually found after the postal code. the postal code is usually 4 digits, or 4 digits followed by a - and 3 more digits.
    - If not found, set to None.


# date_of_admission_UQ:
    - data de admissão na UQ
    - usually in the beginning of the file after the line that contains "Tel:" with or without a telephone number in that line.
    - if not there:
        - search in the text of the admission note.
        - after expressions as "admitido na UQ", or "data de admissão na UQ".
    - return in format dd-mm-yyyy.
    - If not found, set to None.


# origin:
    - look in the text where the patient was transfered from before entering the UQ.
    - it's in the HDA section, história da doença actual.
    - it can be a place in the hospital - unit, emergency room, etc - another hospital, VMER, HELI, etc.


# date_of_discharge:
    - look for it in the discharge note.
    - usualy the fist date in the discharge note.
    - if not look for it after expressions such as "Alta médica:" or "data de alta".
    - if there is no discharge note, look in the death certificate or information for the date of death, which is the date of discharge.
    - return in the format dd-mm-yyyy.
    - If not found, set to None.


# destination:
    - after discharge from the UQ, the patient was transfered to the destination
    - usually another department, unit or service within the hospital
    - often transfer to another hospital
    - can also de transfered to a recovery unit or home


If contradictory data is found, return None.