# https://docs.datastax.com/en/astra-serverless/docs/vector-search/quickstart.html
ASTRA_DB_SECURE_BUNDLE_PATH = 'secure-connect-q-a.zip'
ASTRA_DB_TOKEN_JSON_PATH = 'Q&A-token.json'
ASTRA_DB_KEYSPACE = 'VedantKey'
OPENAI_API_KEY = ''
ASTRA_DB_APPLICATION_TOKEN = "AstraCS:McwjrpCHCRHkTDkPcPnZDStC:9d800dddca2e32dbcd176ffbdcbeb93e3727a9685da688297ee994f0e5d47323"
ASTRA_DB_ID = "eafc27ff-f267-42a4-a669-4389b7b6fdb7"


from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from datasets import load_dataset
import cassio
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthenticator
import json

cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

print("Initializing and Connecting to the Database...")
cloud_config={
    "secure_connect_bundle": ASTRA_DB_SECURE_BUNDLE_PATH
}

with open(ASTRA_DB_TOKEN_JSON_PATH) as f:
    secrets = json.load(f);
ASTRA_DB_APPLICATION_TOKEN = secrets["token"] #? Token is pulled out from the json file.

# auth_provider=PlainTextAuthenticator("token", ASTRA_DB_APPLICATION_TOKEN)
# cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
# astraSession=cluster.connect()

llm = OpenAI(openai_api_key=OPENAI_API_KEY) #?Initializing LLM
myEmbedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

myCassandraVStore = Cassandra(
    embedding=myEmbedding,
    session=None,
    keyspace=ASTRA_DB_KEYSPACE,
    table_name="qa_mini_demo",
)

print('Loading Data from Hugging Face')
myDataset = load_dataset('Biddls/Onion_News', split="train")
headlines = myDataset["text"][:50] #? Getting 50 News and is the list.

with open("headlines.txt","w") as f:
    f.write(str(headlines))

print("\nGenerating embedding and storing in AstraDB")
myCassandraVStore.add_texts(headlines)
print("Inserted %i headlines\n" % len(headlines))
astra_vector_index = VectorStoreIndexWrapper(vectorstore=myCassandraVStore)

first_question = True
while True:
    if first_question:
        query_text = input("\nEnter your question (or type 'quit' to exit): ").strip()
    else:
        query_text = input("\nWhat's your next question (or type 'quit' to exit): ").strip()

    if query_text.lower() == "quit":
        break

    if query_text == "":
        continue

    first_question = False

    print("\nQUESTION: \"%s\"" % query_text)
    answer = astra_vector_index.query(query_text, llm=llm).strip()
    print("ANSWER: \"%s\"\n" % answer)

    print("FIRST DOCUMENTS BY RELEVANCE:")
    for doc, score in myCassandraVStore.similarity_search_with_score(query_text, k=4):
        print("    [%0.4f] \"%s ...\"" % (score, doc.page_content[:84]))