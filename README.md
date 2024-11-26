# PDF Parsing Application

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup Development Environment](#setup-development-environment)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Environment Variables](#2-environment-variables)
  - [3. Docker Installation](#3-docker-installation)
- [Running the Application](#running-the-application)
  - [1. Build and Start Services](#1-build-and-start-services)
  - [2. Accessing Services](#2-accessing-services)
- [API Endpoints](#api-endpoints)
- [Test PDF File](#test-pdf-file)

## Introduction

This application facilitates the parsing of PDF documents by extracting textual content and storing it in a PostgreSQL database. It supports both machine-readable PDFs and scanned image-based PDFs by leveraging PyMuPDF for text extraction and PaddleOCR for optical character recognition. A FastAPI backend provides API endpoints for interaction, while a Vue.js frontend built with Vite offers a user-friendly interface.

## Features

- **PDF Uploading**: Upload PDF files through the frontend or API.
- **Text Extraction**: Extracts text from machine-readable PDFs using PyMuPDF.
- **OCR Support**: Applies PaddleOCR for scanned or image-based PDFs.
- **Real-Time Status Updates**: Uses WebSockets to notify users of processing statuses.
- **Database Management**: Stores extracted text and metadata in PostgreSQL.
- **Frontend Interface**: Interactive UI for managing and previewing parsed PDFs.
- **Admin Interface**: Utilize Adminer for database administration.

## Architecture

- **Frontend**: Vue.js application served via Vite.
- **Backend**: FastAPI application handling API requests and background tasks.
- **Database**: PostgreSQL for storing PDF data and extracted text.
- **Adminer**: Web-based database management tool.
- **Docker Compose**: Orchestrates all services for easy setup and deployment.

## Prerequisites

- **Docker**: Ensure Docker is installed on your machine.
- **Docker Compose**: Typically included with Docker Desktop.

## Setup Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-parsing-app.git
cd pdf-parsing-app
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following content:
but I already created one by default in local side
```env
# .env
DB_NAME=pdf_data
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

### 3. Docker Installation
Ensure Docker and Docker Compose are installed and running on your system.

- **Install Docker**: Follow the Docker Installation Guide.

- **Verify Installation**: 

```
docker --version
docker-compose --version
```

## Running the Application

### 1. Build and Start Services
Use Docker Compose to build and run all services (Front-End, Back-End, Adminer, PostgresSQL):
```
docker-compose up --build
```
This command will build the Docker images for the backend and frontend, set up the PostgreSQL database, and start all services.

### 2. Accessing Services
 - **Frontend**: http://localhost:5173/
 - **Backend API Documentation**: http://localhost:8000/docs
 - **Adminer (Database UI)**: http://localhost:8080/

## API Endpoints

### 1. Upload PDF
- **Endpoint** : `/upload/`
- **Method** : `POST`
- **Description** : Upload a PDF file for parsing 
- **Parameters** : `file` : PDF file to upload
- **Response**:
  - `file_id`: Unique identifier for the uploaded file.
  - `uploaded_at`: Timestamp of the upload.
  - `message`: Status message.
---

### 2. List Uploaded Files
- **Endpoint** : `/files`
- **Method** : `GET`
- **Description** : Retrieves a list of all uploaded files with metadata. 
- **Response**: JSON array containing file details
---

### 3. Preview Extracted Text
- **Endpoint** : `/preview/{file_id}`
- **Method** : `GET`
- **Description** : Fetches the extracted text content of a specific file. 
- **Response**: JSON object containing `file_id` and `text_content`
---

### 4. Delete File
- **Endpoint** : `/delete/{file_id}`
- **Method** : `DELETE`
- **Description** : Deletes a specific file and its associated data from the database. 
- **Parameters** : `file` : PDF file to upload
- **Response**: Confirmation message.
---

### 5. WebSocket for Status Updates
- **Endpoint** : `/ws`
- **Method** : `POST`
- **Description** : Establishes a WebSocket connection to receive real-time status updates on file processing.
---

## Test PDF File
Ensure you have test PDF files located in the `data/pdfs/` directory. These files are used to evaluate the PDF parsing functionality.

**Text-Based PDFs**
- 2406v2-text-based.pdf
- DMTestPdf-text-based.pdf

**Image-Based or Mixed PDFs**
- 2022-image-based.pdf
- 2024-mix-based.pdf