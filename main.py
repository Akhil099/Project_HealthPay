from fastapi import FastAPI, UploadFile, File, HTTPException
import os, hashlib, fitz, asyncio, pydantic
#it is same as object class that helps in making guidelines for input and output for the RestAPI 
from typing import List
from datetime import datetime
from datetime import datetime
from dotenv import load_dotenv
from extraction_strategies import * 
from collections import defaultdict

from langchain_google_genai import ChatGoogleGenerativeAI


app = FastAPI()
load_dotenv()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok = True)

@app.get('/')
def introduction_message():
    return ('Please enter the parameter with /docs in the link')
    
    
@app.post('/process-claim')
async def upload_file(files : List[UploadFile] = File(..., media_type="application/pdf")):  #Here 3 dots in Upload file means for the File class a File is required
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail = "Max of 5 files allowed")
    
    result_list = []
    llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash", temperature = 0)
    
    pages_by_type = defaultdict(list)
    
    strategy_registry = {
        "bill" : BillSummary(),
        "discharge_summary" : DischargeSummary(),
        "insurance_form" : InsuranceSummary(),
        "id" : IdSummary()
    }
    
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail = f"{file.filename} is not a PDF")
        
        timestamp = datetime.now().isoformat()
        
        hash_prefix = hashlib.sha256(f"{file.filename}_{timestamp}".encode()).hexdigest()[:8]
        
        filename = f"{file.filename}_{hash_prefix}"
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            # shutil.copyfileobj(file.file, f)
            f.write(await file.read())
            
        #Extract text from PDF
        
        docs = fitz.open(file_path)
        pages = [page.get_text() for page in docs]
        for i, page_text in enumerate(pages):
            prompt1 =f"""
                You are a document classifier.

                Your job is to classify the page text below into one of the following types:

                - "bill": Only classify as "bill" if the page includes explicit bill summary content such as invoice, hospital receipt, interim bill, Tax Invoice, In Patient Bill, bill of supply, billing summary.
                - "discharge_summary": Only classify as "discharge_summary" if the page includes explicit discharge summary content such as medical summaries including surgery, diagnosis, clinical summary, medications, Patient Details or outcomes.
                - "insurance_form": Only classify as "insurance_form" if the page includes explicit insurance claim content such as claim number, approval status, Health Insurance Policy, Insurance Company, Policy Holder, policy details, cashless investigation or insurer remarks.
                - "id": Only classify as "id" if the page includes explicit id content such as government-issued ID cards such as Aadhaar, PAN, Government of India or insurance membership cards.

                Please return only one word: either "bill", "discharge_summary", "insurance_form", or "id".

                Page text:
                {page_text}
            """
            # print(page_text)

            await asyncio.sleep(10)
            classification = llm.invoke(prompt1).content.strip().lower()
            pages_by_type[classification].append(page_text)
            
    # print(f'Page by type is printed here \n',pages_by_type, '\n\n\n')  
      
    for doc_type, page_text in pages_by_type.items():
        strategy = strategy_registry.get(doc_type)
        
        if not strategy:
            result_list.append({
                "type": doc_type,
                "error": f"No strategy defined for document type: {doc_type}"
            })
            continue

        full_text = "\n".join(page_text)
        try:
            extracted = strategy.extract(llm, full_text)
            extracted["type"] = doc_type  # Ensure type is accurate
        except Exception as e:
            extracted = {
                "type": doc_type,
                "error": f"Extraction failed: {str(e)}"
            }

        result_list.append(extracted)
                
    print(result_list)
    
    valid_result_types = set(strategy_registry.keys())
    
    present_documents = set()
    for res in result_list:
        if isinstance(res, dict) and res.get('type') in valid_result_types:
            present_documents.add(res["type"])
            
    required_documents = {"bill", "discharge_summary", "insurance_form","id"}

    missing_types = list(required_documents - present_documents)
    
    missing_details = []
    
    for res in result_list:
        document_type = res.get('type')
        # if document_type not in strategy_registry:
        #     missing_documents.append(doc_type)
        #     continue
        
        for key, value in res.items():
            if key == "type":
                continue
            if value in [None, "", []]:
                missing_details.append(f'{document_type}_{key}')
    
    if not missing_types and not missing_details:
        claim_decision = {
            'status' : 'approved',
            'reason' : 'all documents are present and data is consistent'
        }
    else:
        claim_decision = {
        'status': 'pending',
        'reason' : 'all documents are not present or data inconsistency'
    }
            
            
    return {
        "message": "Files processed successfully",
        "results": result_list,
        "validation":{
            'missing_documents' : missing_types,
            'missing_details' : missing_details
        },
        'claim_decision' : claim_decision
    }
        