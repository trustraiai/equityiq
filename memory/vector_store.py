from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embedding = OpenAIEmbeddings()

db = FAISS.from_texts(
    ["Initial memory"],
    embedding
)

def store_data(text):
    db.add_texts([text])

def retrieve_data(query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in docs])