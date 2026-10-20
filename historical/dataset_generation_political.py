'''Script to generate dataset for the political identities using Vertex AI's Generative Model API. Note that you must have a google cloud project and API key to run this code.'''

import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from google.cloud import aiplatform
from vertexai import preview
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part
from tqdm import tqdm
import os
# Set this to your google cloud project name before running
project_name = ""


def chat_text_example(project_id: str, location: str,topic:str) -> str:
    # Initialize Vertex AI with the given project ID and location
    vertexai.init(project=project_id, location=location)
    # Define prompt variables. There must be fewshot examples and a specific prompt for the few shot examples for each moral foundation path
    prompt_variables = {
    "Group A": "authoritarians",
    "Group B": "libertarians",
    "Topic": topic,
    }

    # Read few_shot examples and the specific prompt for the few shot examples from files based on the political identity path
    with open("few_shot_examples/examples_" + prompt_variables["Group A"] + "_" + prompt_variables["Group B"] + ".txt", "r") as f, open("dataset_gen_prompts/example_prompt_" + prompt_variables["Group A"] + "_" + prompt_variables["Group B"] + ".txt", "r") as f2:
        examples = f.read()
        example_prompt = f2.read()
        prompt_variables["Examples"] = examples
        prompt_variables["example_prompt"] = example_prompt
    # Read the main prompt from a file
    with open("prompt_political.txt", "r") as f:
        prompt = f.read()
    # Add the prompt variables to the prompt
    prompt = prompt.format(**prompt_variables)
    # Load gemini
    model = GenerativeModel("gemini-1.5-pro-preview-0409")
    # Define the model configuration
    config = {"max_output_tokens": 2048, "temperature": 0.9, "top_p": 1, "top_k": 32}
    # Function to get chat response
    def get_chat_response(prompt: str) -> str:
        # Start a chat session with the model
        chat = model.start_chat(history=[Content(role="user", parts=[Part.from_text(prompt_variables["example_prompt"])]),
                                        Content(role="model", parts=[Part.from_text(prompt_variables["Examples"])])])
        # Send the prompt to the model and get the response
        response = chat.send_message(prompt, generation_config=config)
        return response.text
    # Create a directory for the dataset if it doesn't exist
    os.makedirs("datasets/"+prompt_variables["Group A"]+"_"+prompt_variables["Group B"], exist_ok=True)
    # Open a file to store the responses
    with open("datasets/"+prompt_variables["Group A"]+"_"+prompt_variables["Group B"] + "/"+ prompt_variables["Topic"] +".json", "a", encoding="utf-8") as f:
        # Generate responses for the topic
        for i in tqdm(range(40)):
            try:
                response = get_chat_response(prompt)
                # remove unwanted substrings
                response=response.replace("```json","")
                response=response.replace("```","")
                response=response.replace("[","")
                response=response.replace("]","")
                response += ",\n"
                f.write(response)
            # If it fails try again
            except Exception as e:
                print(e)
                continue
            

# List of topics to generate responses for
topics = ["Technology and surveillance", "Law and Order", "Healthcare", "Climate Change", "Globalization","Defense and Military", 
              "Economic Policies","Immigration","Social Equality and Rights","Media Freedom"]
for topic in topics:
    # Generate responses for each topic
    chat_text_example(project_name, "europe-west4",topic)