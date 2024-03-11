# Imports
from langchain.llms import HuggingFaceTextGenInference
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

inference_server_url = "http://hf-tgi.llm-hosting.svc.cluster.local:3000/"

# Basic llm object definition, no text streaming
llm = HuggingFaceTextGenInference(
    inference_server_url=inference_server_url,
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)

llm("Can you describe Paris in 100 words?")
