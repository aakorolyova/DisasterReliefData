from __future__ import absolute_import

from pathlib import Path

from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.prompts import PromptTemplate

# %%
model = "gpt-3.5-turbo-1106"

# Data consists of PDFs from https://rnli.org/what-we-do/international/international-resources, wikipedia page with emergency numbers per country, and some FEMA pages
docs = SimpleDirectoryReader(
    input_dir=str(Path("data/StaticDocs").absolute())
).load_data()

# %%
index = VectorStoreIndex.from_documents(docs)
query_engine = index.as_query_engine(response_mode="compact")

prompts_dict = query_engine.get_prompts()
print(prompts_dict)

new_summary_tmpl_str = (
    "Context information is below."
    "---------------------"
    "{context_str}"
    "---------------------"
    "Given the context information and not prior knowledge, answer the query."
    "The user is a person in an area hit by a disaster, potentially in distress."
    "You answers must be brief, precise and as actionable as can be based on the context information."
    "Query: {query_str}"
    "Answer: "
)
new_summary_tmpl = PromptTemplate(new_summary_tmpl_str)
query_engine.update_prompts({"response_synthesizer:summary_template": new_summary_tmpl})
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
    response = query_engine.query(question)
    print(question)
    print(response)
    print()
