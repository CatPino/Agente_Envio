import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import Config

def inicializar_vector_store():
    loader = DirectoryLoader('base/', glob="./*.txt", loader_cls=TextLoader)
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=Config.GITHUB_TOKEN,
        base_url=Config.GITHUB_BASE_URL
    )
    return FAISS.from_documents(chunks, embeddings)

vector_store = inicializar_vector_store()

def consultar_informacion_envios(args):
    """
    Esta es la función que el Agente llamará. 
    Recibe un diccionario 'args' con la clave 'query'.
    """
    pregunta = args.get("query")
    
    docs = vector_store.similarity_search(pregunta, k=3)
    
    contexto = "\n".join([doc.page_content for doc in docs])
    return contexto