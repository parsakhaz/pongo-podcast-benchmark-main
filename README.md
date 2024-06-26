# Acquired Podcast RAG System

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system for the Acquired podcast. It allows users to query and retrieve relevant information from podcast transcripts using various vector databases and search technologies. The system includes components for data processing, uploading, and querying using LlamaIndex, Pongo, and Azure Cognitive Search.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Setup](#setup)
4. [Data Processing](#data-processing)
5. [Uploading Data](#uploading-data)
6. [Running Queries](#running-queries)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have the following:

- Python 3.7+
- pip (Python package manager)
- Access to OpenAI API (for embeddings)
- Pinecone account and API key
- Pongo account and API key
- Azure account with Cognitive Search service set up

## Project Structure

The project is organized as follows:

```text
acquired-podcast-rag/
│
├── scripts/
│   ├── upload/
│   │   ├── llamaindex-upload.py
│   │   ├── pongo-upload.py
│   │   └── split-azure-files.py
│   │
│   └── run/
│       ├── llamaindex-run-podcast.py
│       ├── run-pongo.py
│       └── run-azure.py
│
├── acquired_transcripts/
│   └── [podcast transcript files]
│
├── results/
│   └── [output files]
│
└── Acquired Podcast Questions.csv
```

## Setup

1. Clone the repository:

   ```cmd
   git clone https://github.com/your-repo/acquired-podcast-rag.git
   cd acquired-podcast-rag
   ```

2. Create a virtual environment:

   ```python
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:

   ```python
   pip install llama-index pinecone-client openai pongo azure-search-documents datasets
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:

   ```text
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PONGO_SECRET_KEY=your_pongo_secret_key
   AZURE_SEARCH_KEY=your_azure_search_key
   AZURE_SEARCH_ENDPOINT=your_azure_search_endpoint
   AZURE_SEARCH_INDEX=your_azure_search_index_name
   ```

## Data Processing

Before uploading data, you need to process the podcast transcripts:

1. Place all podcast transcript files in the `acquired_transcripts/` directory.

2. For Azure, run the script to split files into chunks:

   ```python
   python scripts/upload/split-azure-files.py
   ```

   This will create chunked files in `acquired_transcripts/chunks/`.

## Uploading Data

### LlamaIndex (Pinecone)

1. Open `scripts/upload/llamaindex-upload.py`.
2. Replace `'YOUR_OAI_KEY'` and `'YOUR_PINECONE_KEY'` with your actual API keys.
3. Run the script:

   ```python
   python scripts/upload/llamaindex-upload.py
   ```

### Pongo

1. Open `scripts/upload/pongo-upload.py`.
2. Replace `'YOUR_PONGO_SECRET'` with your Pongo API key.
3. Run the script:

   ```python
   python scripts/upload/pongo-upload.py
   ```

4. Note the sub-organization ID printed in the console for later use.

### Azure Cognitive Search

1. Ensure you have split the files using `split-azure-files.py`.
2. Use the Azure portal or Azure CLI to create an index and upload the chunked files.

## Running Queries

### LlamaIndex

1. Open `scripts/run/llamaindex-run-podcast.py`.
2. Replace `'YOUR_OPENAI_KEY'` and `'YOUR_PINECONE_KEY'` with your actual API keys.
3. Run the script:

   ```python
   python scripts/run/llamaindex-run-podcast.py
   ```

### Pongo

1. Open `scripts/run/run-pongo.py`.
2. Replace `'YOUR_PONGO_SECRET_KEY'` with your Pongo API key.
3. Set the `sub_org_id` variable to the ID you noted during the upload process.
4. Run the script:

   ```python
   python scripts/run/run-pongo.py
   ```

### Azure Cognitive Search

1. Open `scripts/run/run-azure.py`.
2. Replace `'YOUR_AZURE_INDEX'`, `'YOUR_ENDPOINT_NAME'`, and `'YOUR_AZURE_KEY'` with your Azure Cognitive Search details.
3. Run the script:

   ```python
   python scripts/run/run-azure.py
   ```

## Testing the RAG System

To test the RAG system with queries:

1. Ensure you have completed the data uploading steps for at least one of the methods (LlamaIndex, Pongo, or Azure).
2. Run the corresponding query script (e.g., `llamaindex-run-podcast.py` for LlamaIndex).
3. The script will process questions from `Acquired Podcast Questions.csv` and generate results in the `results/` directory.
4. Review the output files (e.g., `results/llamaindex-benchmark-results.csv`) to see the questions, retrieved context, and answers.

To test with custom queries:

1. Modify the respective run script to accept user input instead of reading from a CSV file.
2. Run the script and enter your query when prompted.
3. The script will return relevant context from the podcast transcripts based on your query.

## Troubleshooting

- If you encounter API rate limits, adjust the `time.sleep()` calls in the scripts to introduce delays between requests.
- For memory issues, try reducing the `max_datapoints` parameter in the processing functions.
- Ensure all API keys and endpoints are correctly set in your `.env` file or directly in the scripts.
- Check that the transcript files are in the correct format and location before running the upload scripts.

For any other issues, consult the documentation of the respective services (OpenAI, Pinecone, Pongo, Azure) or seek help in their community forums.
