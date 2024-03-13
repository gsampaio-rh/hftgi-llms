from kafka import KafkaProducer
import json
import os
import time

# Path to the file containing the chat content
folder_path = "conversation_samples"

# Kafka setup
kafka_server = "localhost:9092"  # Change this to your Kafka server address
producer_topic = "chat"

# Create a KafkaProducer instance
producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

def send_chat_to_kafka(file_path, producer, topic):
    # Read the chat content from the file
    with open(file_path, "r", encoding="utf-8") as file:
        chat_content = file.read()

    # Format the content as a JSON object
    message = {"conversation": chat_content}

    # Send the message to the Kafka topic
    producer.send(topic, value=message)
    producer.flush()  # Ensure the message is sent before the script exits

    print("Chat content sent to Kafka topic.")

# # Execute the function
# send_chat_to_kafka(file_path, producer, producer_topic)


def send_chats_to_kafka(folder_path, producer, topic):
    while True:
        # Get list of files in the specified folder
        file_list = os.listdir(folder_path)

        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                send_chat_to_kafka(file_path, producer, topic)
                # Sleep for 15 seconds before the next iteration
                time.sleep(10)
                print(
                    "Iteration over files completed. Waiting for 15 seconds before the next iteration."
                )

# Execute the function
send_chats_to_kafka(folder_path, producer, producer_topic)
