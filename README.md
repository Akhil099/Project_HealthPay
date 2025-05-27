I was given the task of building a FASTAPI based web service that processes uploaded medical insurance PDF documents and discards any pictures that are uploaded. It extracts structured claim details such as hospital names, billed amounts, diagnoses, and admission/discharge dates using Gemini LLM model and classifies the data by pages

The features that I have included are :


-> Accepts multiple PDF files for batch claim processing

-> Uses LangChain and Gemini (Google Generative AI) for intelligent extraction

-> Supports hospital bill formats, insurance forms, and more

-> Exposes REST endpoints with Swagger UI documentation

-> Securely loads environment variables using .env

As I was assigned the task of only building the backend service, so I have tested my service on FASTAPI docs feature that allows us to test our REST API endpoints. It accepts multiple pdf files and according gives decision on the claims on the documents that are submitted in the pdf


I have taken 4 documents as the base of processing of the claim, mainly hospital bill, insurance form, discharge summary and ID as mentioned in the task description

I have used strategy design pattern to use the same method to extract the contents from the classified files from the pdf and is returned by the LLM in json

I have saved the documents for parsing in a local storage that can be found out in the same Project_HealthPay folder under uploaded_files folder

The Tech Stack that I have used is:

-> Python 3.11

-> FastAPI + Uvicorn

-> PyMuPDF (fitz) for PDF parsing

-> LangChain + Gemini (langchain-google-genai)

-> dotenv for configuration

-> Docker for containerization

Project Structure:

    Project_HealthPay/
    ├── main.py                    # FastAPI server and endpoint logic
    ├── extraction_strategies.py  # PDF parsing and AI-based extraction logic
    ├── requirements.txt          # Python dependencies
    ├── .env                      # Environment variables (e.g., API keys)
    ├── Dockerfile                # Docker image configuration
    ├── .dockerignore             # Docker cleanup rules

I have also added a docker file in this project, and you can build the docker image using the command
     "docker build -t healthpay-app . "

and to run the application, you need to run the command :
    "docker run -p 8000:8000 --env-file .env healthpay-app"

The Environment variables that i have used is a Gemini Api Key





