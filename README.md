# GraphRAG-API
# Knowledge Retrieval and Question-Answering API

This API provides knowledge retrieval and question-answering capabilities on PDF documents using GraphRAG, vector embeddings, and a robust API structure built with FastAPI. It processes PDFs from URLs, extracts their content, and allows users to query the content for information and answers.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
  - [Interactive API Docs](#interactive-api-docs)
  - [Endpoints](#endpoints)
    - [`POST /upload-pdf/`](#post-upload-pdf)
    - [`GET /retrieve`](#get-retrieve)
    - [`GET /answer`](#get-answer)
- [Testing](#testing)
  - [Testing with a Large PDF](#testing-with-a-large-pdf)
- [Error Handling and Edge Cases](#error-handling-and-edge-cases)

---

## Overview
<img width="1482" alt="image" src="https://github.com/user-attachments/assets/1d265b6c-1270-444d-a4b9-5f604de037ba">

This FastAPI application allows users to:

- **Upload PDFs via a URL**: The `/upload-pdf/` endpoint accepts a URL to an online PDF, processes it, and stores its content for retrieval.
- **Retrieve Contextual Information**: The `/retrieve` endpoint allows users to retrieve relevant text chunks from the uploaded PDFs based on a query.
- **Get Answers to Questions**: The `/answer` endpoint uses the retrieved context to generate answers to user queries using OpenAI's GPT-4 model.

The application leverages:

- **GraphRAG**: For building a knowledge graph representing key concepts within the document.
- **LanceDB**: As a vector database to store and manage document embeddings.
- **OpenAI's GPT-4**: For generating embeddings and answering queries.
- **Swagger UI**: For interactive API documentation and testing.

---

## Prerequisites

- **Python**: Version 3.8 or higher.
- **OpenAI API Key**: An API key from OpenAI to access GPT-4.
- **GraphRAG API Key**: An API key for GraphRAG (if required).
- **Git**: For cloning the repository (optional).

---

## Installation

1. **Clone the Repository** (or download the code files):

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Ensure your `requirements.txt` includes all necessary packages:

   ```
   fastapi
   uvicorn
   PyMuPDF  
   requests
   langchain
   lancedb
   openai
   python-dotenv
   graphrag
   ```

---

## Environment Setup

1. **Create a `.env` File**:

   In the root directory of your project, create a `.env` file and add your API keys:

   ```dotenv
   OPENAI_API_KEY=your-openai-api-key
   GRAPHRAG_API_KEY=your-graphrag-api-key
   GRAPHRAG_CONFIG_PATH=/path/to/your/settings.yaml
   GRAPHRAG_DATA_DIR=/path/to/your/output
   ```
   Replace /path/to/your/settings.yaml and /path/to/your/output with the actual paths on your system.

   **Important:** Do not share these API keys publicly or commit them to version control.

2. **Load Environment Variables in Your Code**:

   Ensure your application loads the environment variables. At the top of your main script (`main.py`), include:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

---

## API Documentation

### Interactive API Docs

FastAPI provides an interactive Swagger UI available at `http://127.0.0.1:8000/docs`. You can use this interface to explore and test the API endpoints directly from your browser.

### Endpoints

#### `POST /upload-pdf/`

**Description**: Processes an online PDF from a given URL, assigns a unique document ID, and prepares it for query-based retrieval.

- **Request Body**:

  - `url` (string): The URL to the online PDF document.

  Example:

  ```json
  {
    "url": "https://example.com/document.pdf"
  }
  ```

- **Response**:

  - `message` (string): Status message.
  - `doc_id` (string): The unique document ID assigned.

  Example:

  ```json
  {
    "message": "PDF uploaded and processed",
    "doc_id": "123e4567-e89b-12d3-a456-426614174000"
  }
  ```

#### `GET /retrieve`

**Description**: Accepts a query and a document ID, returning relevant text chunks based on knowledge graph and similarity scores.

- **Query Parameters**:

  - `query` (string): The user's query.
  - `doc_id` (string): The document ID to filter the search.

- **Response**:

  - A list containing text chunks.

  Example:

  ```json
  [
    [
      [
        {
          "page_content": "Relevant text chunk...",
          "metadata": {
            "doc_id": "123e4567-e89b-12d3-a456-426614174000"
          }
        },
        0.95
      ],
      // Additional results...
    ]
  ]
  ```

#### `GET /answer`

**Description**: Accepts a query and a document ID, returning a direct answer generated by the LLM using the retrieved context.

- **Query Parameters**:

  - `query` (string): The user's question.
  - `doc_id` (string): The document ID to filter the search.

- **Response**:

  - `answer` (string): The answer to the user's question.

  Example:

  ```json
  {
    "answer": "The main topics of the course include business valuation techniques, methodologies, and ethical considerations."
  }
  ```


## Testing

### Testing with a Large PDF

Test the API using a large PDF, such as the [CBV Institute Level I Course Notes](https://cbvinstitute.com/wp-content/uploads/2019/12/Level-I-Course-Notes-ENG.pdf).


## Error Handling and Edge Cases

The API includes error handling for various edge cases:

- **Invalid PDF URLs**: If the provided URL does not point to a valid PDF or is inaccessible, the API returns an error message.

- **Unsupported File Formats**: If the file at the URL is not a PDF, the API will return an error.

- **Documents with Insufficient Content**: If the PDF does not contain any extractable text, the API will handle this gracefully.

- **Model Context Length Exceeded**: If the combined length of the context and the query exceeds the model's maximum context length, the API returns an error message advising the user to refine their query.



