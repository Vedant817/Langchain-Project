from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#! CodeTextSplitter allows you to split your code with multiple languages supported.
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS #? A library for efficient similarity search.
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()

video_url = "https://youtu.be/uBJoo6wDRZA?feature=shared"
def create_vector_db_from_youtube_url(video_url: str) -> FAISS:
    loader = YoutubeLoader.from_youtube_url(
        video_url, add_video_info=True
    )
    transcript = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db


#? We are using the response from the db to generate answers to the questions being asked.
def get_response_from_query(db, query, k=4):
    docs = db.similarity_search(query, k=k) #* This is collecting the data from the db related to the query entered.
    docs_page_content= " ".join([d.page_content for d in docs]) #? Docs is a list with 4 elements.

    llm = OpenAI(model = 'text-davinci-003')
    prompt = PromptTemplate(
        input_variables = ["question", docs],
        template="""
        You are a helpful assistant that that can answer questions about youtube videos 
        based on the video's transcript.
        
        Answer the following question: {question}
        By searching the following video transcript: {docs}
        
        Only use the factual information from the transcript to answer the question.
        
        If you feel like you don't have enough information to answer the question, say "I don't know".
        
        Your answers should be verbose and detailed.
        """,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(question = query, docs=docs_page_content)
    #* Passing the parameters for the input_variables while implementing the function.
    response= response.replace("\n","")
    return response
