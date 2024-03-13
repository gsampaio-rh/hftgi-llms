from flask import Flask, Response, stream_with_context, render_template
from kafka import KafkaConsumer
import json

app = Flask(__name__)

TOPIC_NAME="answer"

def create_consumer():
    """Function to create a new KafkaConsumer instance for each request."""
    return KafkaConsumer(
        "answer",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=None,  # Using None or a unique group_id for each consumer can help avoid conflicts
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        session_timeout_ms=6000,
        heartbeat_interval_ms=1000,
    )

@app.route("/stream")
def stream():
    """Route to stream Kafka messages to clients using Server-Sent Events."""

    def generate_messages():
        consumer = create_consumer()  # Create a new consumer instance for this request
        for message in consumer:
            try:
                # Manually deserialize the message value from a JSON string to a dictionary
                message_dict = json.loads(message.value)

                # print(message_dict)

                # Now you can safely use .get() since message_dict is a dictionary
                json_response = message_dict.get("json_response", {})

                json_response["conversation"] = message_dict.get("conversation")

                # Add the 'id' field from the message_dict to the json_response
                if "id" in message_dict:
                    json_response["id"] = message_dict["id"]

                # Check if 'sentiment_analysis' exists and replace it with the value at 'sentiment_analysis.text'
                if "sentiment_analysis" in json_response and "text" in json_response["sentiment_analysis"]:
                    json_response["sentiment_analysis"] = json_response["sentiment_analysis"]["text"]

                # Sending only the json_response part to the client
                yield f"data: {json.dumps(json_response)}\n\n"
            except json.JSONDecodeError:
                # Handle case where message value is not a valid JSON string
                print(f"Error decoding JSON for message: {message.value}")

    return Response(generate_messages(), mimetype="text/event-stream")

@app.route("/messages")
def messages():
    """Renders the initial HTML page."""
    return render_template("messages.html")

@app.route("/nosentiment")
def nosentiment():
    """Renders the initial HTML page."""
    return render_template("no-sentiment.html")

if __name__ == "__main__":
    app.run(debug=True)
