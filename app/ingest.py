from langchain_text_splitters import RecursiveCharacterTextSplitter

def cargar_y_dividir_datos():
    with open("base/tarifas.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(texto)
    return chunks