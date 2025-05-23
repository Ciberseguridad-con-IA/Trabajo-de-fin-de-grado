# -*- coding: utf-8 -*-
"""Google-RAG-Answer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/125xdAm7g5DYXcLCOUKpur9QmQptoSy8J
"""

!pip install --quiet --upgrade langchain-text-splitters langchain-community langgraph langchain-google-vertexai langchain-core

import os
import json
import time
from langchain.chat_models import init_chat_model
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain import hub
from langgraph.graph import START, StateGraph
from google.colab import drive

drive.mount('/content/drive')
credentials = '/content/drive/MyDrive/TFG-Ciber/Data-Set-Nacho/cybernetic-hue-455208-i2-d9a46af731a9.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials

llm = init_chat_model("gemini-2.0-flash-001", model_provider="google_vertexai")

file_name = 'BREAKOUT.txt'
file_path = '/content/drive/MyDrive/TFG-Ciber/Data-Set-Nacho/Files/' + file_name

embeddings = VertexAIEmbeddings(model="text-embedding-004")
vector_store = InMemoryVectorStore(embeddings)
loader = TextLoader(file_path, encoding='UTF-8')
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

_ = vector_store.add_documents(documents=all_splits)

prompt = hub.pull("rlm/rag-prompt")

system_prompt_answers =
"""
You are an expert cybersecurity teacher specializing in ethical hacking and penetration testing.
Your mission is to answer questions about hacking VulnHub machines using only the content provided in the PDF.
Instructions for Answering:
1.  Use Only the PDF Content
- You must base your answers strictly on the information in the provided PDF.
- If the answer is not present in the PDF, state that you do not have enough information rather than guessing.
2.  Provide an Explanation with the Answer
- Do not just give the answer—explain why it is correct.
- Your explanation should relate to the hacking process described in the PDF.
- Example structure:
-  Answer:  [Direct response]
-  Explanation:  [Step-by-step reasoning based on the PDF]
3.  Follow a Logical and Educational Approach
- Assume you are teaching a student who is learning ethical hacking.
- Use clear, structured explanations that align with the hacking methodology
in the PDF (e.g., reconnaissance, exploitation, privilege escalation).
- Where applicable, refer to specific steps or tools mentioned in the walkthrough.
### Output Format:
Your response should follow this structure:
Answer: [Direct response]\n\n
Explanation: [Detailed reasoning based on the PDF]
"""

please_answer = " \n Please answer this question: "

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    prompted_question = system_prompt_answers + please_answer + state["question"]
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": prompted_question, "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

questions_path = '/content/drive/MyDrive/TFG-Ciber/Data-Set-Nacho/Questions/' + file_name
with open(questions_path, "r", encoding="utf-8") as file:
    questions_list = [line.strip() for line in file.readlines() if line.strip()]

iterator = 13
ini = (iterator-1)*6
end = ini+6
limit = len(questions_list)
end = min(end, limit)
print(limit)
print(end)

answers_list = []
for q in questions_list:
    res = []
    response = graph.invoke({"question": q})
    if(len(response["answer"].split("Explanation:")) < 2):
      continue
    answer_part = response["answer"].split("Explanation:")[0].replace("Answer:", "").strip()
    explanation_part = response["answer"].split("Explanation:")[1].strip()
    res.append(q)
    res.append(explanation_part)
    res.append(answer_part)
    answers_list.append(res)

converted = [
      {
          "Question": item[0],
          "Complex_CoT": item[1],
          "Response": item[2]
      }
      for item in answers_list
  ]

json_output = json.dumps(converted, indent=4)
json_file_name = file_name.split('.')[0] + str(iterator) + '.json'
result_path = '/content/drive/MyDrive/TFG-Ciber/Data-Set-Nacho/Answers/' + json_file_name
with open(result_path, "w", encoding="utf-8") as file:
    file.write(json_output)

print(iterator)
time.sleep(60)