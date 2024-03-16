#####################################################################
# Imports 
#####################################################################
from flask import Flask, request, make_response
from dotenv import load_dotenv
import os
from llama_index.core import (
    VectorStoreIndex, 
    ServiceContext,
    set_global_service_context
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from semantic_router.layer import RouteLayer
from semantic_router import Route
import chromadb
from semantic_router.encoders import HuggingFaceEncoder
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import json

#####################################################################
# constants 
#####################################################################
db_path = '../chroma_db'
path_prompt_folder = '../prompt/'
chroma_collection_name = 'base_de_conhecimento'

#####################################################################
# Models definition
#####################################################################
# get api key
load_dotenv()
api_key = os.getenv("OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# llm model object
llm = OpenAI()
# embedding model object
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
)
# encoder for semantic router
encoder = HuggingFaceEncoder()

#####################################################################
# Service Context
#####################################################################
service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model=embed_model,
  system_prompt="You are an AI assistant answering questions."
)

set_global_service_context(service_context)

#####################################################################
# Prompt definition
#####################################################################
with open(path_prompt_folder + 'bate_papo.txt', 'r') as file:
    
    prompt_bate_papo = file.read()
    
with open(path_prompt_folder + 'rag.txt', 'r') as file:
    
    prompt_rag = file.read()
    
#####################################################################
# functions
#####################################################################
def create_index_from_chroma_col(db_path):
    # load from disk
    
    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_collection(chroma_collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    
    return index 

def create_route_layer():
    
    rota_bate_papo = Route(
            name="bate-papo",
            utterances=[
            "Olá",
            "Olá",
            "Ei",
            "Quem é?",
            "Olá tudo bem?",
            "Bom Dia!",
            "E você como está?",
            "Tudo em ordem?",
            "Como vai?",
            "Tudo bem?",
            "Como vão as coisas?",
            "Que bom ver-te!",
            "Olá, quanto tempo!",
            "E você, está tudo bem?",
            "Como está sendo o seu dia?",
            "Olá, foi como se fosse o seu dia?",
            "Fala amigo!",
            "Saudação!",
            "Olá bom!",
            "Boa tarde!",
            "Boa noite!",
            "Como vai a vida?",
            "Tudo tranquilo?",
            "Olá tudo bem?",
            "E você, está tudo bem?",
            "Você aqui?",
            "Como vai esse sorriso?",
            "Pronto para a conversa?",
            "Conversaremos?",
            "Algo novo?",
            "Diga-me mais sobre você.",
            "E você, novidades?",
            "O que me contas de bom?",
            "Como você tem estado?",
            "Tudo bem aí?",
            "Algum plano para hoje?",
            "Então, como vai?",
            "Vamos conversar?",
            "Um prazer te conhecer.",
            "Olá, você está pronto para hoje?",
            "E você, como está seu humor?",
            "Você sempre vem aqui?",
            "Olá, eu posso ajudar você?",
            "Como foi seu fim de semana?",
            "Espero que esteja bem!",
            "Olá"
            ]
        )

    routes = [
        rota_bate_papo]

    rl = RouteLayer(encoder=encoder, routes=routes)
    
    return rl

def get_response(question, conversation_context, use_rl = False ,route_layer = rl):
    
    
    if use_rl and rl(question).name == 'bate-papo':
        
        print('rota bate-papo')
        
        prompt_formated = prompt_bate_papo.format(question = question)
        
        
    else:
        
        print('rota None')
        
        nodes = retriever.retrieve(question)

        context_str = ''
        for node in nodes:
            # print({(node.text.split('\n')[0]).replace('Nome: ','')})
            nome = (node.text.split('\n')[0]).replace('Nome: ','')
                    
            context_str +=f"\n<reference>\n"
            
            context_str +=f"<metadata>\n"
            context_str += str(node.metadata)+'\n'
            context_str +=f"</metadata>\n"
            
            
            context_str +=f"<content>\n"
            context_str += node.text+'\n'
            context_str +=f"</content>\n"
            
            context_str +=f"</reference>\n"
            
        prompt_formated = prompt_rag.format(context = context_str, question = question, conversation_history=conversation_context)
        
    response = llm.complete(prompt_formated)
    response_text = response.text.split('</answer>')[0]
    
    return prompt_formated, response_text

def trata_payload_frontend(payload_front):

    payload = {
        'mensagens': [x['content'] for x in payload_front['inputs'][0][1:]]
    }

    return payload



index = create_index_from_chroma_col(db_path)
retriever = index.as_retriever(similarity_top_k = 3)


rl = create_route_layer()




#####################################################################
# app flask
#####################################################################

app = Flask(__name__)
@app.route('/ask', methods = ['POST', 'OPTIONS'])
def charla():
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        resp = make_response("")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        resp.headers['Access-Control-Expose-Headers'] = '*'
        resp.headers['X-Requested-With'] = '*'
        resp.headers['Content-Type'] = 'application/json'
        return resp
        
    request_json = request.get_json(force= True, silent=True)
    print("Request", request_json)
    question=request_json['inputs'][0][-1]['content']
    print("Question: ", question)
    
    # Fetch conversation context
    payload_front = json.loads(request.data)
    payload = trata_payload_frontend(payload_front)
    payload_lista_mensagens = list(payload.items())[0][1]
    payload_tratado = ""
    for indice, mensagem in enumerate(payload_lista_mensagens[:-1]):
        if indice % 2 == 0:
            mensagem_tratada = f"""
            usuario: {mensagem}
            """
            payload_tratado += mensagem_tratada 
        else:
            mensagem_tratada = f"""
            asistente: {mensagem}
            """
            payload_tratado += mensagem_tratada
    # get user question
    question = payload_lista_mensagens[-1]
    
    
    prompt_formated, response_text = get_response(
        question = question, 
        conversation_context = payload_tratado
        )
    
    print(prompt_formated)

    # Format result output
    result = [{'generation': {'role': 'assistant', 'content': f'{response_text}'}}]
    
    ### Send Flask app response
    resp = make_response(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    resp.headers['Access-Control-Expose-Headers'] = '*'
    resp.headers['X-Requested-With'] = '*'
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/check')
def check():
    return "Everything running ok! 666"

if __name__ == "__main__":
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Fargate, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080)


