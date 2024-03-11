# Imports
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceTextGenInference
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate

def read_conversation_file(file_path):
    """Reads content from a specified file path."""
    with open(file_path, "r", encoding="utf-8") as file:
        txt = file.read()
    return txt

inference_server_url = "http://hf-tgi-server.llms.svc.cluster.local:3000/"

# template = """<s>[INST] <<SYS>>
# You are a helpful, respectful and honest assistant.
# You will be given a question you need to answer, and a context to provide you with information. You must answer the question based as much as possible on this context.
# Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

# If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
# <</SYS>>

# Question: {question}
# Context: {context} [/INST]
# """

template = """
<s>[INST] <<SYS>>
As an assistant, your task is to analyze a WhatsApp conversation and extract essential information in a structured and concise manner. Focus on identifying and summarizing the main points without repetition. The required information includes the respondent's name, contact details (email and phone number), their affiliation or the relevant organization (if mentioned), the specific issue or service they are addressing, the location related to the issue, the main points of their complaint, and their desired outcome.

You should structure your response by clearly labeling each piece of information and ensuring that there is no repetition. If similar points are made more than once in the conversation, summarize them in a single statement. Your goal is to provide a clear and concise summary of the conversation's key details.

Based on the following conversation, please extract and summarize the necessary information:

{conversation}

Your response should respect privacy, accuracy, and ethical guidelines. Simplify the information while maintaining its original meaning and context. Avoid making assumptions beyond the data provided.
<</SYS>>[/INST]
"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

embeddings = HuggingFaceEmbeddings()

# Basic llm object definition, no text streaming
llm = HuggingFaceTextGenInference(
    inference_server_url=inference_server_url,
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.1,
    repetition_penalty=1.175,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)

chain = QA_CHAIN_PROMPT | llm

file_path = "sample_chat.txt"
conversation_text = read_conversation_file(file_path)

chain.invoke({"conversation": conversation_text})

# context = ""

# # question = "Can you describe Paris in 200 words?"
# # chain.invoke({"question": question, "context": context})

# # Interactive questions and answers
# while True:
#     query = input("\nEnter a query: ")
#     if query == "exit":
#         break
#     # Get the answer from the chain
#     chain.invoke({"question": query, "context": context})

# # llm_streaming(
#     "Can you describe Paris in 200 words?", callbacks=[StreamingStdOutCallbackHandler()]
# )
