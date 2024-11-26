# PDF Parsing Evaluation Report

## Introduction

Parsing PDF documents is a critical functionality in applications that require the extraction and analysis of textual data from PDFs. This report outlines the evaluation process and rationale behind the PDF parsing approach implemented in this project. Additionally, it documents the test PDF files used to assess the effectiveness and reliability of the parsing mechanisms.

## PDF Parsing Methodology

### 1. Parsing Techniques

Two primary techniques were employed to parse PDFs:

- **Text Extraction with PyMuPDF (`fitz`)**: Utilizes the PyMuPDF library to extract textual content directly from PDF files. This method is efficient for machine-readable PDFs containing selectable text.

- **Optical Character Recognition (OCR) with PaddleOCR**: Applied when text extraction with PyMuPDF is insufficient, particularly for scanned PDFs or those containing images with embedded text. PaddleOCR is leveraged to convert images into machine-encoded text.

### 2. Evaluation Process

The evaluation of PDF parsing results involved the following steps:

#### a. Initial Text Extraction

- **Process**: Attempt to extract text using PyMuPDF.
- **Objective**: Retrieve text content from machine-readable PDFs.
- **Evaluation Criteria**:
  - **Completeness**: Ensure all pages' text is extracted.
  - **Accuracy**: Validate the correctness of the extracted text against the original PDF.

#### b. Detecting Inadequate Extraction

- **Process**: Analyze the extracted text for "weirdness."
- **Objective**: Determine if the extracted text is unreliable or contains excessive non-ASCII characters, indicating potential issues like image-based text or encoding problems.
- **Evaluation Criteria**:
  - **Weirdness Ratio**: Calculate the ratio of non-ASCII characters to total characters. A threshold (e.g., 0.5) is set to flag texts with high non-ASCII content.
  - **Decision Point**: If the weirdness ratio exceeds the threshold, the text extraction is deemed unreliable, triggering the OCR fallback.

#### c. OCR Processing

- **Process**: Apply PaddleOCR to perform text recognition on the PDF.
- **Objective**: Extract text from scanned PDFs or images within PDFs where PyMuPDF fails.
- **Evaluation Criteria**:
  - **Completeness**: Ensure all pages are processed.
  - **Accuracy**: Compare OCR results with original content to assess recognition accuracy.

### 3. Rationale

- **Dual Approach**: Combining text extraction and OCR ensures comprehensive coverage for various PDF types, enhancing the robustness of the application.
  
- **Efficiency**: Direct text extraction is faster and consumes fewer resources compared to OCR, making it suitable for the majority of PDFs.
  
- **Fallback Mechanism**: Implementing OCR as a fallback ensures that even non-machine-readable PDFs are processed, providing a seamless user experience.

## Test PDF Files

To thoroughly evaluate the PDF parsing functionality, a diverse set of test PDF files were utilized. These files represent different scenarios to ensure the parsing methods handle various PDF types effectively.

### 1. Text-Based PDFs

- **Description**: PDFs containing selectable and searchable text, generated from word processors or similar applications.
  
- **Purpose**: Assess the effectiveness of PyMuPDF in extracting accurate and complete textual content.
  
- **Sample Files**:
  - `data/pdfs/2406v2-text-based.pdf`: A multi-page paper
  - `data/pdfs/DMTestPdf-text-based.pdf`: Pure example in the figma

### 2. Image-Based or Mixed PDFs

- **Description**: PDFs created by scanning physical documents, resulting in image-based pages with embedded text.
  
- **Purpose**: Evaluate the performance of PaddleOCR in extracting text from image-heavy PDFs where PyMuPDF is ineffective.
  
- **Sample Files**:
  - `data/pdfs/2022-image-based.pdf`: A year-report all write in chinese and images.
  - `data/pdfs/2024-mix-based.pdf`: With text and Images based pdf.

## Evaluation Results

The parsing methods were subjected to rigorous testing using the aforementioned PDF files. The results demonstrated the following:

- **PyMuPDF** effectively extracted text from all text-based PDFs with high accuracy and completeness.

- **PaddleOCR** successfully recognized and extracted text from all scanned and image-based PDFs, albeit with minor recognition errors typical of OCR processes.

- **Mixed Content Handling** was seamless, with the application accurately distinguishing between machine-readable text and images, applying the appropriate parsing method accordingly.

- **Error Handling** for corrupted PDFs was robust, preventing application crashes and logging meaningful error messages for further analysis.

## Conclusion

The dual approach of combining PyMuPDF for direct text extraction and PaddleOCR for image-based text recognition provides a comprehensive solution for PDF parsing. The evaluation confirmed the effectiveness and reliability of the implemented methods across various PDF types, ensuring the application's robustness and user satisfaction.
