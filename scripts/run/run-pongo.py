import csv
import requests
import time 
import pongo

# Sub-organization ID for Pongo API
sub_org_id = '' # Paste sub-org-id from previous step

# Initialize Pongo client with your secret key
pongo_client = pongo.PongoClient('YOUR_PONGO_SECRET_KEY')

"""
This script performs a Retrieval-Augmented Generation (RAG) task using the Pongo API.
It processes questions from a CSV file, retrieves relevant context using Pongo,
and saves the results (question, answer, and context) to a new CSV file.

The script is part of a larger application for the Acquired podcast,
focusing on retrieving and storing relevant information for podcast-related questions.

Key components:
1. Pongo API integration for context retrieval
2. CSV file handling for input questions and output results
3. Retry logic for API calls
4. Context string building from retrieved documents

Usage:
1. Set the sub_org_id variable with the appropriate Pongo sub-organization ID
2. Replace 'YOUR_PONGO_SECRET_KEY' with your actual Pongo API secret key
3. Run the script to process questions and generate results
"""

def get_sub_orgs():
    """
    Fetch and display available sub-organizations if sub_org_id is not provided.
    
    This function is useful for debugging and setup purposes. It allows users
    to view available sub-organizations before setting the sub_org_id.

    Returns:
        None

    Side effects:
        Prints the list of available sub-organizations to the console
        Exits the script if sub_org_id is not set
    """
    if sub_org_id == '':
        print("Available sub-organizations:")
        print(pongo_client.get_sub_orgs().json()) 
        print("\nPlease set the sub_org_id variable with one of the above IDs.")
        quit(0)

def initialize_results_file():
    """
    Check if the results file exists. If not, create it and add headers.
    
    This function ensures that the output file is properly initialized before
    writing results. It creates the file with appropriate headers if it doesn't exist.

    Returns:
        bool: True if file already exists, False if a new file was created

    Side effects:
        Creates a new CSV file '../results/pongo-acquired-benchmark-results.csv' if it doesn't exist
    """
    file_path = '../results/pongo-acquired-benchmark-results.csv'
    file_exists = False
    try:
        with open(file_path, 'r') as file:
            file_exists = True
    except FileNotFoundError:
        pass

    if not file_exists:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["question", 'answer', 'context'])
        print(f"Created new results file: {file_path}")

    return file_exists

def process_datapoints(starting_datapoint_index=0, max_datapoints=5000):
    """
    Main processing function to iterate through datapoints, perform Pongo searches,
    and write results to the output file.

    This function reads questions from an input CSV file, retrieves relevant context
    using the Pongo API, and writes the results to an output CSV file. It supports
    resuming processing from a specific index and limiting the number of datapoints processed.

    Args:
        starting_datapoint_index (int): Index to start processing from (default: 0)
        max_datapoints (int): Maximum number of datapoints to process (default: 5000)

    Returns:
        None

    Side effects:
        Writes processed results to '../results/pongo-acquired-benchmark-results.csv'
        Prints progress updates to the console
    """
    datapoint_index = starting_datapoint_index

    with open('../results/pongo-acquired-benchmark-results.csv', 'a', newline='') as file, \
            open('../../Acquired Podcast Questions.csv', 'r') as reader:
        writer = csv.writer(file)
        csv_reader = csv.DictReader(reader)

        for datapoint in csv_reader:
            if datapoint_index >= max_datapoints:
                print(f"Reached maximum datapoints ({max_datapoints}). Exiting.")
                quit(0)
            
            if datapoint_index % 10 == 0:
                print(f'Processing datapoint index: {datapoint_index}')
            
            if datapoint_index < starting_datapoint_index:
                datapoint_index += 1
                continue

            question = datapoint['question']
            answer = datapoint['answer']

            context_string = perform_pongo_search(question)
            
            writer.writerow([question, answer, context_string])
            datapoint_index += 1

def perform_pongo_search(query):
    """
    Perform a search query using the Pongo API with retry logic.

    This function sends a search query to the Pongo API and retrieves relevant documents.
    It includes a retry mechanism to handle temporary API failures.

    Args:
        query (str): The search query

    Returns:
        str: The context string built from retrieved documents

    Raises:
        RuntimeError: If the Pongo query fails after a retry

    Side effects:
        Prints API response status to the console
    """
    has_retried = False
    while True:
        response = pongo_client.search(query=query, sub_org_id=sub_org_id)
        print(f"Pongo API response status: {response.ok}")

        if response.ok:
            break
        elif has_retried:
            raise RuntimeError('Failed to complete Pongo query after retry. Please try again later.')
        else:
            print("Pongo API request failed. Retrying in 1 second...")
            time.sleep(1)
            has_retried = True

    docs = response.json()
    return build_context_string(docs)

def build_context_string(docs, max_length=10000):
    """
    Build a context string from retrieved documents.

    This function combines the text from multiple retrieved documents into a single
    context string, with source numbering and formatting. It limits the total length
    of the context string to avoid excessively large outputs.

    Args:
        docs (list): List of document dictionaries from Pongo API
        max_length (int): Maximum length of the context string (default: 10000)

    Returns:
        str: The built context string

    Note:
        The function adds source numbering and separators between document texts.
    """
    context_string = ''
    source_index = 1
    for doc in docs:
        if len(context_string) <= max_length:
            context_string += f'\n\n----------\n\nSource #{source_index}: \n"'
            context_string += doc['text'] + '"'
            source_index += 1
        else:
            break  # Stop adding documents if max_length is reached
    return context_string

# Main execution
if __name__ == "__main__":
    print("Starting Pongo RAG processing for Acquired podcast questions")
    get_sub_orgs()
    file_existed = initialize_results_file()
    if file_existed:
        print("Results file already exists. Appending new results.")
    else:
        print("New results file created.")
    process_datapoints()
    print("Processing completed successfully.")

