import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from app.config import Config

def ejecutar_pipeline_rag(pregunta_usuario):
    loader = DirectoryLoader('base/', glob="./*.txt", loader_cls=TextLoader)
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documentos)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=Config.GITHUB_TOKEN,
        base_url=Config.GITHUB_BASE_URL
    )

    vector_store = FAISS.from_documents(chunks, embeddings)

    llm = ChatOpenAI(
        model=Config.MODEL_NAME,
        api_key=Config.GITHUB_TOKEN,
        base_url=Config.GITHUB_BASE_URL,
        temperature=Config.TEMPERATURE
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}) 
    )
    respuesta = qa_chain.invoke(pregunta_usuario)
    return respuesta["result"]