
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCUMENTS_DIR = Path("documents")
VECTOR_DB_DIR = "vector_db"

# Load every PDF
documents = []

for pdf_file in DOCUMENTS_DIR.glob("*.pdf"):
    print(f"Loading: {pdf_file.name}")

    loader = PyPDFLoader(str(pdf_file))
    pdf_pages = loader.load()

    # Keep track of which PDF each page came from
    for page in pdf_pages:
        page.metadata["source"] = pdf_file.name

    documents.extend(pdf_pages)

if not documents:
    raise ValueError("No PDF files found in the documents folder.")

print(f"Loaded {len(documents)} pages from your PDFs.")

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks.")

# Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create the vector database
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECTOR_DB_DIR
)

print("Vector database created successfully!")
