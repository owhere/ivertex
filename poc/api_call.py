import os
from dotenv import load_dotenv
from google import genai
from google.auth.exceptions import RefreshError

# 1. Load configuration
load_dotenv()

# 2. Logic to convert the "True"/"False" string into a real Boolean
# This checks if the text is exactly "true" (ignoring case)
use_vertex = os.getenv("USE_VERTEX", "False").lower() == "true"

# 3. Initialize the Client using your env variables
client_kwargs = {"vertexai": use_vertex}

if use_vertex:
    # Enterprise mode: Needs project and location
    client_kwargs["project"] = os.getenv("PROJECT_ID")
    client_kwargs["location"] = os.getenv("LOCATION")
else:
    # Developer mode: Needs ONLY the API key
    client_kwargs["api_key"] = os.getenv("GOOGLE_API_KEY")

# 3. Initialize the Client using "argument unpacking" (the ** syntax)
client = genai.Client(**client_kwargs)

backend = "Vertex AI" if use_vertex else "Gemini API"
print(f"--- Successfully connected via: {backend} ---")

# 4. Create a stateful chat session
# This object will store the history of the conversation automatically.
chat = client.chats.create(model="gemini-2.0-flash")

if use_vertex:
    print(f"--- Project ID: {client_kwargs["project"]} | Location: {client_kwargs["location"]} ---")
else:
    # Tip: Don't print your full API key for security reasons!
    print(f"--- Authentication: API Key (AI Studio) ---")

print("Gemini Interactive Chat (Type 'exit' or 'quit' to stop)")

while True:
    # Get user input from the terminal
    user_input = input("\nYou: ")

    # Check if the user wants to quit
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    try:
        # Send the message to the chat session
        response = chat.send_message(user_input)
        
        print(f"\nGemini: {response.text}")

    except RefreshError:
        print("\n[!] AUTH ERROR: Please run 'gcloud auth application-default login' in your terminal.")
        break
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")
