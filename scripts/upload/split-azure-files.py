# This script is part of a larger repository for an acquired podcast RAG (Retrieval-Augmented Generation) retrieval application.
# It processes transcript files by splitting them into smaller chunks suitable for upload to Azure blob storage.
# The chunking process ensures that each segment is of a manageable size for efficient processing and retrieval.

import os

def split_into_chunks(file_path, approx_chunk_size=900):
    """
    Splits a transcript file into smaller chunks, preparing them for upload to Azure blob storage.

    This function reads a transcript file, divides it into chunks of approximately 900 characters each,
    and saves these chunks as separate files. Each chunk starts with the original file's name as a title,
    followed by the content. The function ensures that chunks do not break in the middle of a line.

    Args:
        file_path (str): The path to the transcript file to be processed.
        approx_chunk_size (int, optional): The approximate size of each chunk in characters. Defaults to 900.

    Returns:
        None

    Side effects:
        - Creates a 'chunks' directory if it doesn't exist.
        - Writes multiple chunk files to the 'chunks' directory.
        - Prints status messages for each chunk written.
    """
    # Create 'chunks' directory if it does not exist
    if not os.path.exists('chunks'):
        os.makedirs('chunks')

    # Extract filename without the .txt extension for use in chunk titles
    base_filename = os.path.splitext(os.path.basename(file_path))[0]

    # Open and read the entire file content
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.readlines()

    current_chunk = [f"Title: {base_filename}\nBody:\n"]
    current_count = 0
    chunk_index = 0

    for line in file_content:
        current_count += len(line)
        if current_count >= approx_chunk_size:
            # Write the current chunk to a file
            chunk_file_name = f"{file_path}/chunks/{base_filename}-{chunk_index}.txt"
            with open(chunk_file_name, 'w', encoding='utf-8') as chunk_file:
                chunk_file.write(''.join(current_chunk))
            print(f"Chunk {chunk_index} written to {chunk_file_name}")

            # Reset for the next chunk
            current_chunk = [f"Title: {base_filename}\nBody:\n"]
            current_count = len(line)
            chunk_index += 1
        current_chunk.append(line)

    # Write any remaining content as a final chunk
    if len(current_chunk) > 1:  # There is more than just the header
        chunk_file_name = f"{file_path}/chunks/{base_filename}-{chunk_index}.txt"
        with open(chunk_file_name, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(''.join(current_chunk))
        print(f"Final chunk {chunk_index} written to {chunk_file_name}")

def process_all_txt_files():
    """
    Processes all .txt files in the 'acquired_transcripts' directory.

    This function iterates through all .txt files in the '../../acquired_transcripts' directory,
    applying the split_into_chunks function to each file. It's designed to batch process
    multiple transcript files, preparing them for upload to Azure blob storage.

    The function is a crucial part of the podcast RAG retrieval application pipeline. It ensures
    that all acquired podcast transcripts are properly segmented for efficient storage and retrieval
    in the Azure blob storage system.

    Args:
        None

    Returns:
        None

    Side effects:
        - Calls split_into_chunks for each .txt file in the directory.
        - Creates chunk files for each processed transcript.
        - Prints processing status for each file (indirectly through split_into_chunks).

    Note:
        - This function assumes that all .txt files in the 'acquired_transcripts' directory
          are valid podcast transcripts that need to be processed.
        - The function does not handle exceptions, so any issues with file reading or writing
          will cause the script to terminate.
    """
    for file in os.listdir('../../acquired_transcripts'):
        if file.endswith('.txt'):
            file_path = os.path.join('../../acquired_transcripts', file)
            print(f"Processing file: {file}")
            split_into_chunks(file_path)
            print(f"Finished processing: {file}\n")

# Execute the main processing function
if __name__ == "__main__":
    print("Starting to process all transcript files...")
    process_all_txt_files()
    print("All transcript files have been processed and split into chunks.")
