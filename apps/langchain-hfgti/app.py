# Imports
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceTextGenInference
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from kafka import KafkaConsumer, KafkaProducer
import json

# Kafka setup
kafka_server = "localhost:9092"  # Change this to your Kafka server address
consumer_topic = "chat"
producer_topic = "answer"

consumer = KafkaConsumer(
    consumer_topic,
    bootstrap_servers=[kafka_server],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="chat-group",
    # value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

def read_conversation_file(file_path):
    """Reads content from a specified file path."""
    with open(file_path, "r", encoding="utf-8") as file:
        txt = file.read()
    return txt

# inference_server_url = "http://hf-tgi-server.llms.svc.cluster.local:3000/"

inference_server_url = "http://localhost:3000/"

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
)

chain = QA_CHAIN_PROMPT | llm

# file_path = "sample_chat.txt"
# conversation_text = read_conversation_file(file_path)

# answer = chain.invoke({"conversation": conversation_text})

# print(answer)

for message in consumer:
    try:
        # Decode the message value from bytes to a string and then load it as JSON
        conversation_data = json.loads(message.value.decode('utf-8'))
        conversation_text = conversation_data['conversation']

        print("CHAT: ->", conversation_text)

        # Process the conversation with the chain
        response = chain.invoke({"conversation": conversation_text})

        print("RESPOSTA: ->",response)

        # Prepare the result to be sent to the 'answer' topic
        result = {"conversation": conversation_text, "response": response}

        # Send the processed result to the Kafka 'answer' topic
        producer.send(producer_topic, value=result)
        print("Processed and sent conversation to 'answer' topic.")

    except Exception as e:
        print(f"Error processing message: {e}")
