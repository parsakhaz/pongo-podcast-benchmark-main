# Import necessary libraries and modules
from llama_index import SimpleDirectoryReader
from llama_index.vector_stores import PineconeVectorStore
from llama_index.node_parser import SentenceSplitter
from llama_index.schema import TextNode
from llama_index.extractors import (
    QuestionsAnsweredExtractor,
    TitleExtractor,
)
import pinecone
from llama_index.embeddings import OpenAIEmbedding

def initialize_embedding_model():
    """
    Initialize and return an OpenAI embedding model.

    This function sets up the OpenAI embedding model used to generate
    embeddings for text chunks. It uses the 'text-embedding-3-large' model
    with 3072 dimensions.

    Returns:
        OpenAIEmbedding: An instance of the OpenAI embedding model.
    """
    return OpenAIEmbedding(model="text-embedding-3-large", api_key='YOUR_OAI_KEY', dimensions=3072)

def setup_pinecone():
    """
    Set up Pinecone credentials and initialize the environment.

    This function initializes the Pinecone client with the provided API key
    and environment settings. Pinecone is used as the vector database to
    store and retrieve embeddings.
    """
    pinecone_api_key = 'YOUR_PINECONE_KEY'
    pinecone_environment = 'us-east1-gcp'
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)

def create_pinecone_index(index_name):
    """
    Create a new Pinecone index for storing podcast embeddings.

    This function creates a new index in Pinecone with the specified name
    and configuration. The index is used to store and search for podcast
    transcript embeddings.

    Args:
        index_name (str): The name of the Pinecone index to create.

    Returns:
        pinecone.Index: An instance of the created Pinecone index.
    """
    pinecone.create_index(index_name, dimension=3072, metric="euclidean", pod_type="p1")
    return pinecone.Index(index_name)

def initialize_vector_store(pinecone_index):
    """
    Initialize a vector store using the Pinecone index.

    This function creates a PineconeVectorStore instance, which will be used
    to efficiently store and retrieve embeddings.

    Args:
        pinecone_index (pinecone.Index): The Pinecone index to use for the vector store.

    Returns:
        PineconeVectorStore: An instance of the vector store.
    """
    return PineconeVectorStore(pinecone_index=pinecone_index)

def process_transcripts(directory_path):
    """
    Process podcast transcripts from a specified directory.

    This function reads transcript files, splits them into chunks, and
    creates TextNodes for each chunk. It uses a SentenceSplitter for
    chunking the text into manageable pieces.

    Args:
        directory_path (str): Path to the directory containing transcript files.

    Returns:
        list: A list of TextNode objects representing the processed transcript chunks.
    """
    reader = SimpleDirectoryReader(directory_path)
    text_splitter = SentenceSplitter(
        chunk_size=280,
        chunk_overlap=50,
        separator=" ",
    )
    nodes = []

    for docs in reader.iter_data():
        cur_doc = docs[0]
        cur_text_chunks = text_splitter.split_text(cur_doc.text)

        for text_chunk in cur_text_chunks:
            cur_node = TextNode(text=text_chunk)
            cur_node.metadata['file_name'] = cur_doc.metadata['file_name']
            nodes.append(cur_node)

    return nodes

def generate_embeddings(nodes, embed_model):
    """
    Generate embeddings for a list of TextNodes.

    This function takes a list of TextNodes and an embedding model, then
    generates and assigns embeddings to each node based on its content
    and metadata.

    Args:
        nodes (list): A list of TextNode objects to process.
        embed_model (OpenAIEmbedding): The embedding model to use for generating embeddings.
    """
    print('Generating embeddings...')
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding

def main():
    """
    Main function to orchestrate the podcast transcript processing and embedding generation.

    This function coordinates the entire process of reading podcast transcripts,
    generating embeddings, and storing them in a Pinecone vector database. It's part
    of a larger RAG (Retrieval-Augmented Generation) system for the Acquired podcast,
    facilitating efficient retrieval during question-answering or information retrieval tasks.
    """
    # Initialize embedding model
    embed_model = initialize_embedding_model()

    # Set up Pinecone
    setup_pinecone()

    # Create and initialize Pinecone index
    index_name = 'oai-large-podcast'
    pinecone_index = create_pinecone_index(index_name)

    # Initialize vector store
    vector_store = initialize_vector_store(pinecone_index)

    # Process transcripts
    nodes = process_transcripts("../../acquired_transcripts")

    # Generate embeddings
    generate_embeddings(nodes, embed_model)

    # Add processed nodes to the vector store
    vector_store.add(nodes)

    print("Transcript processing and embedding generation completed successfully.")

if __name__ == "__main__":
    main()

# Note: This script is part of a larger RAG (Retrieval-Augmented Generation) system
# for the Acquired podcast. It processes podcast transcripts, generates embeddings,
# and stores them in a vector database (Pinecone) for efficient retrieval during
# question-answering or information retrieval tasks.
