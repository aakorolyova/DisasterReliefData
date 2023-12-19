from pathlib import Path

from langchain.agents.agent_toolkits import (
    create_conversational_retrieval_agent,
    create_retriever_tool,
)
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# Data consists of PDFs from https://rnli.org/what-we-do/international/international-resources, wikipedia page with emergency numbers per country, and some FEMA pages

llm = ChatOpenAI(temperature=0.7)
path = path = Path("data/StaticDocs")
docs = []
for f in path.absolute().iterdir():
    docs.extend(PyPDFLoader(str(f)).load())
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
chunked_documents = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(chunked_documents, embeddings)

llm = ChatOpenAI(model="gpt-3.5-turbo")
chain = load_qa_chain(llm, chain_type="stuff")


retriever = db.as_retriever()
tool = create_retriever_tool(
    retriever,
    "search_disaster_relief",
    "Searches and returns documents regarding disaster relief.",
)
tools = [tool]
agent_executor = create_conversational_retrieval_agent(llm, tools, verbose=True)  # type: ignore


# %%
questions = [
    "What emergency numbers do I call in the USA?",
    "I need emergency shelter, how do I find one?",
    "Somebody is bleeding here, how can I help them?",
    "How do I help bleeding?",
    "How do I help someone with a broken leg?",
    "My area is prone to flooding, how can I prepare?",
    "How do I escape from water in case of flood?",
    "I am caught up in flood and no help is available, how can I rescue myself?",
    "I am caught up in flood and no help is available, how do I get to safety?",
    "I am caught up in flood and no help is available, what do I do?",
]


for question in questions:
    response = agent_executor({"input": question})
    print(question)
    print(response)
    print()
