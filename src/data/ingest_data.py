from llama_index.readers.smart_pdf_loader import SmartPDFLoader
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    ServiceContext,
    StorageContext,
    set_global_service_context
)
import chromadb
from dotenv import load_dotenv
import os

#####################################################################
# Constants
#####################################################################
chroma_collection_name = 'base_de_conhecimento'
db_path = '../chroma_db'
path_docs = '../../data/raw/'

#####################################################################
# Model Config
#####################################################################
load_dotenv()
api_key = os.getenv("OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# llm model object
llm = OpenAI(model = 'gpt-35-turbo')

# create embedding model object
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
)

service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model=embed_model,
  system_prompt="You are an AI assistant answering questions."
)

set_global_service_context(service_context)

#####################################################################
# Read docs
#####################################################################

llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
pdf_loader = SmartPDFLoader(llmsherpa_api_url=llmsherpa_api_url)

documents = SimpleDirectoryReader(path_docs, recursive=True, file_extractor = {'pdf': pdf_loader}).load_data()


#####################################################################
# Create chroma storage
#####################################################################

db = chromadb.PersistentClient(path=db_path)
# save to disk
chroma_collection = db.create_collection(chroma_collection_name)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context, 
    embed_model=embed_model,
    service_context = service_context,
    show_progress = True
)