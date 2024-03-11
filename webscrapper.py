import requests
from bs4 import BeautifulSoup as bs
from nltk.tokenize import word_tokenize
import shortuuid
import chromadb
chroma_client = chromadb.Client()


collection = chroma_client.create_collection(name="knwoledge_base")



#url = 'https://www.uj.ac.za'

def upload_data_to_vectordb(url , project_id):

    response = requests.get(url)
    documents = []
    documents_ids = []
    metadata = []


    if response.status_code == 200:
        try:
            soup = bs(response.text, 'html.parser')

            text_content = soup.get_text()

            words = word_tokenize(text_content)
            # Split text into paragraphs
            #paragraphs = text_content.split('\n\n')

            # Set the desired number of words per chunk
            words_per_chunk = 60

            # Split text into paragraphs of approximately 300 words each
            paragraphs = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]
            # Print or use the paragraphs as needed
            for i, paragraph in enumerate(paragraphs, 1):
                #print(f"Paragraph {i}:\n{' '.join(paragraph)}\n")
                # Generate a short UUID
                short_uuid = shortuuid.uuid()
                documents.append(f"{' '.join(paragraph)}")
                documents_ids.append(short_uuid)
                metadata.append({"user_id": project_id})

            # add the documents to the vector database
            collection.add(
                documents=documents,
                metadatas=metadata,
                ids=documents_ids
            )

            print("document added")

        except Exception as error:
            print(error)

    else:
        print("failed to fetch data")

def get_related_data_from_vectordb(user_input , project_id):

    result = collection.query(
    query_texts = [user_input],
    n_results = 5,
    where={"project_id":project_id}
    )
    print("got the document")
    return result