from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
import fitz  
import os
from concurrent.futures import ProcessPoolExecutor
from graphrag.cli.main import _index_cli
from pathlib import Path
from graphrag.cli.query import run_global_search , run_local_search
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
import uuid
import requests
from dotenv import load_dotenv
load_dotenv()



embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model='gpt-4o')
db_path = "./"
# Initialize LanceDB with the local URI
vector_store = LanceDB(
    uri=f"file://{db_path}",
    embedding=embeddings,
    table_name='langchain_test'
)

app = FastAPI()

def run_index_cli():
    _index_cli(root=Path("."), config=Path("/Users/mariemksontini/Desktop/GraphRag/settings.yaml"))

@app.post("/upload-pdf/")
async def upload_pdf(url: str):
    # Ensure the ./input and ./static directories exist
    os.makedirs('./input', exist_ok=True)
    os.makedirs('./static', exist_ok=True)
    doc_id = str(uuid.uuid4())

    # Download the PDF from the provided URL
    pdf_response = requests.get(url)
    if pdf_response.status_code != 200:
        return {"error": "Failed to download the PDF from the provided URL."}
    
    # Save the downloaded PDF to a temporary location
    pdf_filename = f"{doc_id}.pdf"
    pdf_path = f"./docs/{pdf_filename}"
    with open(pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_response.content)
    
    # Open the PDF file and extract text
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
    
    # Save the extracted text to a .txt file
    txt_filename = f"{doc_id}.txt"
    txt_path = f"./input/{txt_filename}"
    with open(txt_path, "w") as txt_file:
        txt_file.write(text)
    
    # Optionally, clean up the temporary PDF file
    os.remove(pdf_path)

    # Similarity work 
    loader = TextLoader(txt_path)
    documents = loader.load()

    documents = CharacterTextSplitter().split_documents(documents)
    for doc in documents:
        doc.metadata = {"doc_id": doc_id}
    
    # Add documents to the vector store
    vector_store.add_documents(documents=documents, metadata={"doc_id": doc_id})

    # Run _index_cli in a separate process to avoid asyncio conflicts
    with ProcessPoolExecutor() as executor:
        await run_in_threadpool(executor.submit, run_index_cli)
    
    return {"message": "PDF uploaded and processed", "doc_id": doc_id}

@app.get("/retrieve")
def retrieve(query,doc_id: str = None):
    # _query_cli(SearchType.DRIFT, root=Path(), query="hello")
    context = []
    graphragGlobal = run_global_search(Path("/Users/mariemksontini/Desktop/GraphRag/settings.yaml"), data_dir=Path('/Users/mariemksontini/Desktop/GraphRag/output'),  root_dir=Path('.'), community_level=2, streaming=False, query=query, response_type="multiple paragraphs")
    context.append(graphragGlobal[0][:100])
    graphragLocal = run_local_search(Path("/Users/mariemksontini/Desktop/GraphRag/settings.yaml"), data_dir=Path('/Users/mariemksontini/Desktop/GraphRag/output'),  root_dir=Path('.'), community_level=2, streaming=False, query=query, response_type="multiple paragraphs")
    context.append(graphragLocal[0][:100])
    if doc_id:
        retrieveRAG = vector_store.similarity_search_with_relevance_scores(
            query=query, 
            filter={"metadata.doc_id": doc_id}
        )
    else:
        retrieveRAG = vector_store.similarity_search_with_relevance_scores(
        query=query, 
        filter={"metadata.doc_id": doc_id},
        k=3
)
    
    context.append(retrieveRAG)
    return context

@app.get("/answer")
def ansewr(query,doc_id: str = None):
    context = retrieve(query,doc_id)
    print(f"this should be the context from normal rag {context[1]}")
    response = llm.invoke(input=f"answer this question {query} using this context {context}")
    return response.content 
