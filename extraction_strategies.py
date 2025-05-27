import json, re

class ExtractionStrategy:
    async def extract(self, llm, page_text:str) -> dict:
        raise NotImplementedError

class BillSummary(ExtractionStrategy):
    def extract(self, llm, page_text:str) -> dict:
        prompt = f"""
            You are an intelligent document parser. Given the following hospital document page, extract ONLY the requested fields and return strictly valid JSON.

            Extract these fields:
            - type: "bill"
            - hospital_name
            - grand_total
            - date_of_service (in YYYY-MM-DD)

            Return strictly parsable JSON:
                - No markdown formatting (no ```json)
                - Keys in double quotes
                - No explanation or additional text

            Page text:
            \"\"\"
            {page_text}
            \"\"\"

            Return JSON only:
        """
        
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        cleaned = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "type": "bill",  # or the correct type
                "error": "Invalid JSON returned",
                "raw_response": raw
            }
            

class DischargeSummary(ExtractionStrategy):
    def extract(self, llm, page_text) -> dict:
        
        prompt = f"""
            You are an intelligent document parser. Given the following hospital document page, extract ONLY the requested fields and return strictly valid JSON.

            Extract these fields:
            - type: "discharge_summary"
            - patient_name
            - diagnosis
            - admission_date
            - discharge_date
            - admission_date

            Return strictly parsable JSON:
                - No markdown formatting (no ```json)
                - Keys in double quotes
                - No explanation or additional text

            Page text:
            \"\"\"
            {page_text}
            \"\"\"

            Return JSON only:
        """
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        cleaned = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "type": "discharge_summary",  # or the correct type
                "error": "Invalid JSON returned",
                "raw_response": response.content
            }
        
    
class InsuranceSummary(ExtractionStrategy):
    def extract(self, llm, page_text) -> dict:
        prompt = f"""
            You are an intelligent document parser. Given the following hospital document page, extract ONLY the requested fields and return strictly valid JSON.

            Extract these fields:
            - type: "insurance"
            - claimNumber
            - claim_submission
            
            Notes:
                - If status is **not explicitly mentioned**, but a claim number and a claim amount or approval is found, infer:
                - claim_submission : "submitted"

            Return strictly parsable JSON:
                - No markdown formatting (no ```json)
                - Keys in double quotes
                - No explanation or additional text

            Page text:
            \"\"\"
            {page_text}
            \"\"\"

            Return JSON only:
        """
        
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        cleaned = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "type": "insurance",  # or the correct type
                "error": "Invalid JSON returned",
                "raw_response": response.content
            }

class IdSummary(ExtractionStrategy):
    def extract(self, llm, page_text) -> dict:
        prompt = f"""
            You are an intelligent document parser. Given the following hospital document page, extract ONLY the requested fields and return strictly valid JSON.

            Extract these fields:
            - type: "id"
            - patient_name
            -identification_number

            Return strictly parsable JSON:
                - No markdown formatting (no ```json)
                - Keys in double quotes
                - No explanation or additional text

            Page text:
            \"\"\"
            {page_text}
            \"\"\"

            Return JSON only:
        """
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        cleaned = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "type" : "id",
                "error": "Invalid JSON returned",
                "raw_response": response.content
            }
        