from datasets import load_dataset
from llama_index import VectorStoreIndex
from llama_index.vector_stores import PineconeVectorStore
import pinecone
from llama_index.embeddings import HuggingFaceEmbedding
import csv
from openai import OpenAI
import openai
from llama_index.node_parser import SentenceSplitter
from llama_index import ServiceContext
from llama_index.embeddings import OpenAIEmbedding
import time

# Initialize the embedding model using OpenAI's text embedding model
# This model is used to convert text into high-dimensional vectors
embed_model = OpenAIEmbedding(model="text-embedding-3-large", api_key='YOUR_OPENAI_KEY', dimensions=3072)

# Initialize Pinecone with API key and environment
# Pinecone is used as a vector database to store and retrieve embeddings
pinecone_api_key = 'YOUR_PINECONE_KEY'
pinecone_environment = 'us-east1-gcp'
pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)

# Define the name of the Pinecone index
# This index will store the podcast transcript embeddings
index_name = 'oai-large-podcast'

# Connect to the Pinecone index
pinecone_index = pinecone.Index(index_name)

# Create a vector store using the Pinecone index
# This allows us to interact with the Pinecone index using LlamaIndex
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Initialize a text splitter to chunk text into manageable pieces
# This is crucial for processing long podcast transcripts
text_splitter = SentenceSplitter(
    chunk_size=1024,  # Maximum size of each chunk in characters
    separator=" ",    # Separator to use for splitting
    chunk_overlap=128 # Overlap between chunks to maintain context
)

# Create a service context with the embedding model and text splitter
# This context is used by LlamaIndex for various operations
service_context = ServiceContext.from_defaults(llm=None, embed_model=embed_model, text_splitter=text_splitter)

# Create a vector store index using the vector store and service context
# This index allows for efficient similarity search
index = VectorStoreIndex.from_vector_store(vector_store, service_context=service_context)

# Create a retriever from the index to retrieve top-k similar documents
# This will be used to find relevant podcast segments for each question
retriever = index.as_retriever(similarity_top_k=10)

def check_results_file_exists():
    """
    Check if the results file already exists.
    
    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        with open('../results/llamaindex-benchmark-results.csv', 'r') as file:
            return True
    except FileNotFoundError:
        return False

def create_results_file():
    """
    Create the results file and write the header if it doesn't exist.
    """
    with open('../results/llamaindex-benchmark-results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["question", 'answer', 'context'])

def process_questions(max_datapoints=5000):
    """
    Process questions from the input CSV file, retrieve relevant podcast segments,
    and write the results to the output CSV file.

    Args:
        max_datapoints (int): Maximum number of datapoints to process before stopping.
    """
    # Initialize variables for tracking progress
    vectorized_questions = []
    starting_datapoint_index = 0
    datapoint_index = starting_datapoint_index  # Long-running task so enable stopping and starting partway through

    # Open the results file in append mode and the questions file in read mode
    with open('../results/llamaindex-benchmark-results.csv', 'a', newline='') as file, \
            open('../../Acquired Podcast Questions.csv', 'r') as reader:
        writer = csv.writer(file)
        csv_reader = csv.DictReader(reader)

        # Iterate over each datapoint in the questions file
        for datapoint in csv_reader:
            # Stop processing if the datapoint index exceeds the maximum
            if datapoint_index >= max_datapoints:
                print(f"Reached maximum datapoints ({max_datapoints}). Stopping.")
                break
            
            # Print the current datapoint index every 10 datapoints for progress tracking
            if datapoint_index % 10 == 0:
                print('datapoint index: ' + str(datapoint_index))
            
            # Skip datapoints until reaching the starting index
            if datapoint_index < starting_datapoint_index:
                datapoint_index += 1
                continue

            # Extract the question and answer from the current datapoint
            question = datapoint['question']
            answer = datapoint['answer']

            # Retrieve documents relevant to the question using the LlamaIndex retriever
            docs = retriever.retrieve(question)
            context_string = build_context_string(docs)

            # Write the question, answer, and context to the results file
            writer.writerow([question, answer, context_string])

            # Increment the datapoint index
            datapoint_index += 1

def build_context_string(docs, max_context_length=10000):
    """
    Build a context string from the retrieved documents.

    Args:
        docs (list): List of retrieved documents from LlamaIndex.
        max_context_length (int): Maximum length of the context string in characters.

    Returns:
        str: A formatted context string containing content from the retrieved documents.
    """
    context_string = ''
    source_index = 1

    for doc in docs:
        if len(context_string) <= max_context_length:
            context_string += f'\n\n----------\n\nSource #{source_index}: \n"'
            context_string += doc.text + '"'
            source_index += 1
        else:
            break

    return context_string

# Main execution block
if __name__ == "__main__":
    # Check if the results file exists, create it if it doesn't
    if not check_results_file_exists():
        create_results_file()

    # Process questions and generate results
    process_questions()

