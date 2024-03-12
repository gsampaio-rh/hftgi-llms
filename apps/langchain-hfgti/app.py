# Imports
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceTextGenInference
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from kafka import KafkaConsumer, KafkaProducer
import json
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Inference Server Setup
# inference_server_url = "http://hf-tgi-server.llms.svc.cluster.local:3000/"
inference_server_url = "http://localhost:3000/"

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


def convert_to_json(output):
    # Extract the 'text' field which contains the structured information
    structured_text = output.get("text", "")

    # Define the keys we expect to find in the structured text
    keys = [
        "Name",
        "Email",
        "Phone Number",
        "Department",
        "Issue",
        "Service",
        "Additional Information",
        "Outcomes",
    ]

    # Initialize an empty dictionary to hold our extracted data
    data_dict = {}

    # Split the structured text by lines, then iterate over each line
    for line in structured_text.split("\n"):
        # For each line, check if it contains one of the keys
        for key in keys:
            if line.strip().startswith(f"- **{key}**"):
                # Extract the value by removing the key part from the line
                value = line.split(f"- **{key}**:")[1].strip()
                # Handle special case for "Not available" or similar phrases
                if value.lower() in ["not available", "não disponível"]:
                    value = None
                # Add the key-value pair to our dictionary
                data_dict[key.replace(" ", "_").lower()] = value

    # Convert the dictionary to a JSON string
    json_output = json.dumps(data_dict, indent=4, ensure_ascii=False)
    return json_output

template = """
        Given the conversation below, extract key information in a structured and concise manner. The goal is to parse out identifiable details such as personal names, email addresses, phone numbers, and any specific concerns or requests mentioned. This extraction should culminate in a structured JSON output that includes the following fields:

        - **Name**: The name(s) of the person(s) involved.
        - **Email**: Email address(es) mentioned.
        - **Phone Number**: Phone number(s) provided.
        - **Location**: Any specific locations mentioned in relation to the issue or service.
        - **Department**: The department or organization related if specified.
        - **Issue**: Brief description of the main issue(s) discussed.
        - **Service**: Specific service(s) mentioned in connection with the issue.
        - **Additional Information**: Any other relevant details or stakeholders mentioned.
        - **Detailed Description**: A comprehensive summary of the complaint or request, including any specific outcomes desired.

        The response should adhere to privacy and ethical guidelines, simplifying the information while preserving its original context and meaning. Assumptions beyond the provided data should be avoided.

        Conversation Transcript:
        {conversation}

        Note: Ensure your response is concise, avoiding repetition. If similar points are made more than once, summarize them in a single statement, focusing on providing a clear and structured summary of the conversation's key details.
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

llm_chain = LLMChain(prompt=QA_CHAIN_PROMPT, llm=llm)

# file_path = "sample_chat.txt"
# conversation_text = read_conversation_file(file_path)
# answer = chain.invoke({"conversation": conversation_text})
# print(answer)

for message in consumer:
    try:
        # Decode the message value from bytes to a string and then load it as JSON
        conversation_data = json.loads(message.value.decode('utf-8'))
        conversation_text = conversation_data['conversation']

        # Generate a unique ID for the conversation
        conversation_id = str(uuid.uuid4())

        logging.info(f"Conversation ID: {conversation_id}")
        logging.info(f"CHAT: -> {conversation_text}")

        # Process the conversation with the chain
        response = llm_chain.invoke({"conversation": conversation_text})

        # logging.info(f"RESPONSE: -> {response}")

        # Convert the structured response to JSON
        json_response = convert_to_json(response)

        # Convert the json_response string back to a dictionary for inclusion
        json_response_dict = json.loads(json_response)

        # Prepare the result dictionary with the conversation ID, the conversation text,
        # and the structured JSON response
        result = {
            "id": conversation_id,
            "conversation": conversation_text,
            "json_response": json_response_dict
        }

        # Serialize the 'result' dictionary to a JSON-formatted string
        result_json = json.dumps(result, indent=4, ensure_ascii=False)

        # Log the JSON-formatted string of 'result'
        logging.info(f"Result JSON: -> {result_json}")

        # Send the processed result to the Kafka 'answer' topic
        producer.send(producer_topic, value=result_json)
        logging.info("Processed and sent conversation to 'answer' topic.")

    except Exception as e:
        logging.error(f"Error processing message: {e}", exc_info=True)
