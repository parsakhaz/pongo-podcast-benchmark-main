from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import time
import csv

def initialize_azure_search_client(index_name, endpoint_name, key):
    """
    Initialize and return an Azure Search Client with the provided credentials.

    This function sets up the connection to Azure Cognitive Search, which is used
    for retrieving relevant documents based on input queries. It's a crucial
    component in the RAG (Retrieval-Augmented Generation) system for the Acquired
    podcast application.

    Args:
        index_name (str): The name of the Azure Search index containing the podcast transcripts.
        endpoint_name (str): The endpoint URL for the Azure Search service.
        key (str): The API key for authenticating with Azure Search.

    Returns:
        SearchClient: An initialized Azure Search client ready for querying the index.

    Raises:
        ValueError: If any of the input parameters are empty or invalid.
    """
    if not all([index_name, endpoint_name, key]):
        raise ValueError("All parameters (index_name, endpoint_name, key) must be provided.")
    return SearchClient(endpoint_name, index_name, AzureKeyCredential(key))

def create_results_file_if_not_exists(file_path):
    """
    Check if the results file exists, and create it with a header if it doesn't.

    This function ensures that the output file for storing RAG results is properly
    initialized. It's part of the data management aspect of the Acquired podcast
    RAG application.

    Args:
        file_path (str): The path to the results file.

    Returns:
        bool: True if the file was created, False if it already existed.

    Side effects:
        Creates a new CSV file with headers if it doesn't exist.

    Raises:
        IOError: If there's an issue creating or writing to the file.
    """
    try:
        with open(file_path, 'r'):
            return False
    except FileNotFoundError:
        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["question", "true_answer", 'context'])
            return True
        except IOError as e:
            raise IOError(f"Error creating results file: {e}")

def process_questions(search_client, input_file_path, output_file_path, max_datapoints=5000):
    """
    Process questions from the input CSV file, retrieve relevant documents using Azure Search,
    and write the results to the output CSV file.

    This function is the core of the RAG pipeline for the Acquired podcast application.
    It reads questions from an input file, uses Azure Cognitive Search to find relevant
    context from podcast transcripts, and prepares the data for further processing or
    analysis.

    Args:
        search_client (SearchClient): The initialized Azure Search client.
        input_file_path (str): Path to the input CSV file containing questions.
        output_file_path (str): Path to the output CSV file for storing results.
        max_datapoints (int): Maximum number of datapoints to process before stopping.

    Side effects:
        Writes processed data to the output CSV file.
        Prints progress updates to the console.

    Raises:
        FileNotFoundError: If the input file is not found.
        csv.Error: If there's an issue reading or writing CSV data.
    """
    datapoint_index = 0

    try:
        with open(output_file_path, 'a', newline='') as file, \
                open(input_file_path, 'r') as reader:
            writer = csv.writer(file)
            csv_reader = csv.DictReader(reader)

            for datapoint in csv_reader:
                if datapoint_index >= max_datapoints:
                    print(f"Reached maximum datapoints ({max_datapoints}). Stopping.")
                    break

                if datapoint_index % 10 == 0:
                    print(f'Processing datapoint index: {datapoint_index}')

                question = datapoint['question']
                answer = datapoint['answer']

                # Retrieve documents relevant to the question
                docs = search_client.search(question)
                
                context_string = build_context_string(docs)

                # Create the OpenAI query string using the context
                openai_query_string = f'Please use ONLY the sources at the bottom of this prompt to give a short, concise answer the following question.\n\nQuestion: "{question}"{context_string}'

                # Write the question, answer, and context to the results file
                writer.writerow([question, answer, openai_query_string])

                datapoint_index += 1

    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file_path}")
    except csv.Error as e:
        raise csv.Error(f"CSV processing error: {e}")

def build_context_string(docs, max_context_length=12000, max_sources=10):
    """
    Build a context string from the retrieved documents.

    This function formats the content from retrieved documents into a structured
    context string. It's crucial for preparing the data for the language model
    in the RAG system of the Acquired podcast application.

    Args:
        docs (list): List of retrieved documents from Azure Search.
        max_context_length (int): Maximum length of the context string in characters.
        max_sources (int): Maximum number of sources to include in the context.

    Returns:
        str: A formatted context string containing content from the retrieved documents.

    Note:
        The function limits the context based on both character length and number of sources
        to ensure the resulting string is manageable for further processing.
    """
    context_string = ''
    source_index = 1
    
    for doc in docs:
        if len(context_string) <= max_context_length and source_index <= max_sources:
            context_string += f'\n\n----------\n\nSource #{source_index}: \n"'
            context_string += doc['content'] + '"'
            source_index += 1
        else:
            break

    return context_string

# Main execution block
if __name__ == "__main__":
    # Azure Search configuration
    index_name = 'YOUR_AZURE_INDEX'
    endpoint_name = 'YOUR_ENDPOINT_NAME'
    key = 'YOUR_AZURE_KEY'

    # Initialize Azure Search Client
    search_client = initialize_azure_search_client(index_name, endpoint_name, key)

    # File paths
    results_file_path = '../results/azure-benchmark-results.csv'
    questions_file_path = '../../Acquired Podcast Questions.csv'

    # Create results file if it doesn't exist
    create_results_file_if_not_exists(results_file_path)

    # Process questions and generate results
    process_questions(search_client, questions_file_path, results_file_path)

    print("Azure Search RAG processing completed for Acquired podcast questions.")
