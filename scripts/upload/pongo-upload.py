import uuid
import requests
import time
import pongo
import os

# Pongo API secret key for authentication
# This key is used to authenticate requests to the Pongo API
# It should be kept secure and not shared publicly
PONGO_SECRET = 'YOUR_PONGO_SECRET'

# Initialize Pongo client with the secret key
# This client will be used for all interactions with the Pongo API
# It encapsulates the authentication and provides methods for API operations
pongo_client = pongo.PongoClient(PONGO_SECRET)

# Starting index for tracking upload progress
# This is used to keep track of how many datapoints have been uploaded
# Useful for resuming uploads in case of interruptions
starting_index = 0
datapoint_index = starting_index

def create_sub_org():
    """
    Creates a new sub-organization in Pongo.
    
    This function is used to create a separate space within Pongo for organizing
    and managing podcast transcripts. It's useful for isolating this dataset
    from other data that might exist in the main organization.
    
    In the context of the podcast RAG retrieval application, this sub-organization
    will contain all the uploaded podcast transcripts, making it easier to manage
    and search through this specific dataset.
    
    Returns:
        str: The ID of the newly created sub-organization.
    
    Raises:
        requests.exceptions.RequestException: If there's an error in the API call.
    """
    sub_org_id = pongo_client.create_sub_org('Podcast Sub Org').json()['sub_org_id']
    print(f"Uploading to Pongo sub org with ID {sub_org_id}. Save this for searching later")
    return sub_org_id

def upload_transcripts(sub_org_id):
    """
    Uploads podcast transcripts to the specified Pongo sub-organization.
    
    This function iterates through all .txt files in the 'acquired_transcripts' directory,
    reads their content, and uploads each transcript to Pongo with associated metadata.
    It's a crucial part of the data ingestion process for the podcast RAG retrieval application.
    
    The function performs the following steps:
    1. Iterates through .txt files in the 'acquired_transcripts' directory.
    2. Reads the content of each file.
    3. Extracts the title from the filename.
    4. Uploads the transcript to Pongo with metadata including data group, parent ID, and source.
    5. Prints progress and updates the datapoint index.
    
    Args:
        sub_org_id (str): The ID of the sub-organization to upload to.
    
    Raises:
        RuntimeError: If an error occurs during the upload process.
        IOError: If there's an issue reading the transcript files.
    
    Note:
        This function uses a global variable 'datapoint_index' to track progress.
        In a production environment, consider using a more robust progress tracking method.
    """
    global datapoint_index
    try:
        transcript_dir = "../../acquired_transcripts"
        for filename in os.listdir(transcript_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(transcript_dir, filename)
                with open(file_path, 'r') as file:
                    data = file.read()
                    title = filename[:-4]  # Remove '.txt' extension
                    
                    # Upload transcript to Pongo with metadata
                    # The metadata helps in organizing and retrieving the transcripts later
                    pongo_client.upload(
                        data=data,
                        metadata={
                            'data_group': 'podcast',  # Categorizes the data as podcast transcripts
                            'parent_id': title,       # Uses the filename (without extension) as a unique identifier
                            'source': title           # Indicates the source of the transcript
                        },
                        sub_org_id=sub_org_id
                    )
                    print(f'Uploaded {title}')
                    datapoint_index += 1
    except RuntimeError as e:
        print(e)
        print(f'Failed at datapoint index: {datapoint_index}')
        quit(0)

# Main execution
if __name__ == "__main__":
    # Create a new sub-organization for this upload session
    # This ensures that all transcripts uploaded in this run are grouped together
    sub_org_id = create_sub_org()
    
    # Upload all transcripts to the newly created sub-organization
    # This is the main data ingestion step for the podcast RAG retrieval application
    upload_transcripts(sub_org_id)

