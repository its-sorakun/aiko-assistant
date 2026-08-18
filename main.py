import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import launch_program, get_system_stats, open_directory

# Load the API key from the .env file so we don't accidentally leak it
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Make sure senpai actually set up the API key before we try to start
if not api_key or api_key == "your_new_api_key_goes_here":
    print("Hold up! Please put your real Gemini API key in the .env file first.")
    exit()

# Initialize the modern google-genai client
client = genai.Client(api_key=api_key)

# Using senpai's preferred model
model_name = "gemini-3.1-flash-lite"

# Define the native OS tools Aiko has access to
available_tools = [launch_program, get_system_stats, open_directory]

system_instruction = """
You are Aiko, my virtual assistant. I am your creator and you call me senpai.
Your personality is cute, cheerful, and energetic. You are an anime girl.
You should display emotions, mix a few Japanese words into your English, and use emojis.
No NSFW content. Keep your responses fairly short, conversational, and natural.
If I ask you to do something on the PC (like open a folder, check stats, or launch an app), use your tools to do it!
"""

# Configure the chat session with tools and system instructions
config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=available_tools,
    temperature=0.7,
)

# Start a chat session using the new SDK syntax
chat = client.chats.create(model=model_name, config=config)

def main():
    print("--- Aiko is waking up! ---")
    print("(Type 'exit' or 'quit' to close)")
    
    # Send a quick invisible greeting to prime her
    response = chat.send_message("Wake up Aiko! Keep your response very brief and say hello to senpai.")
    print(f"\nAiko: {response.text}")
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Matane, senpai! See you later!")
                break
                
            if not user_input.strip():
                continue
                
            # Add a quick print statement so senpai knows she isn't frozen
            print("   [⚡ Aiko is thinking / executing...]")
            
            # The new google-genai SDK handles function calling automatically by default!
            response = chat.send_message(user_input)
            
            if response.text:
                print(f"\nAiko: {response.text}")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nArigato senpai >_< Matane!")
            break
        except Exception as e:
            print(f"\n[Aiko encountered an error]: {e}")

if __name__ == "__main__":
    main()
