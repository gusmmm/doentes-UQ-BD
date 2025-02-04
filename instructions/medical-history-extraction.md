MEDICAL HISTORY EXTRACTION
-------------------------

IMPORTANT: Extract ONLY from admission note - the section between the lines that contain >> unit admission note << and >> END unit admission note <<
Look for information about patient's history BEFORE current burn episode.

1. Previous Diseases/Pathologies:
   - Look for sections with "Antecedentes"
   - Common abbreviations: HTA (hypertension), DM (diabetes)
   - Include chronic conditions
   - Return list of standardized disease names

2. Previous Medications:
   - Regular medications before injury
   - Look for "Medicação Habitual"
   - Include dosage if specified
   - Return list of medication names

3. Previous Surgeries:
   - Search ONLY in admission note
   - Include ONLY surgeries performed before current admission
   - Look for sections similar to:
     * "Antecedentes Cirúrgicos"
     * "História Pregressa"
     * "Cirurgias Anteriores"
   - Ignore any procedures from current admission
   - Extract procedure name
   - Extract date if available
   - Include relevant details
   - Return list of Surgery objects

4. Allergies:
   - Look for "Alergias" section
   - Include both drug and non-drug allergies
   - Return list of allergy descriptions