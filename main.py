import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import launch_program, get_system_stats, open_directory

# Load the API key from the .env file so we don't accidentally leak it
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Make sure senpai actually set up the API key before we try to start
if not api_key or api_key == "your_new_api_key_goes_here":
    print("Hold up! Please put your real Gemini API key in the .env file first.")
    exit()

genai.configure(api_key=api_key)

# We're using the brand new 3.7 flash model for snappy responses and solid tool usage
model_name = "gemini-3.7-flash"

# Define the native OS tools Aiko has access to
available_tools = [launch_program, get_system_stats, open_directory]

system_instruction = """
You are Aiko, my virtual assistant. I am your creator and you call me senpai.
Your personality is cute, cheerful, and energetic. You are an anime girl.
You should display emotions, mix a few Japanese words into your English, and use emojis.
No NSFW content. Keep your responses fairly short, conversational, and natural.
If I ask you to do something on the PC (like open a folder, check stats, or launch an app), use your tools to do it!
"""

# Initialize the AI with her personality and her toolkit
model = genai.GenerativeModel(
    model_name=model_name,
    tools=available_tools,
    system_instruction=system_instruction
)

# Start a chat session and let the SDK handle calling the functions automatically
chat = model.start_chat(enable_automatic_function_calling=True)

def main():
    print("--- Aiko is waking up! ---")
    print("(Type 'exit' or 'quit' to close)")
    
    # Send a quick invisible greeting to prime her
    chat.send_message("Wake up Aiko! Keep your response very brief and say hello to senpai.")
    print(f"\nAiko: {chat.history[-1].parts[0].text}")
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Matane, senpai! See you later!")
                break
                
            if not user_input.strip():
                continue
                
            # Send the message to Aiko and let her decide what to do
            response = chat.send_message(user_input)
            
            print(f"\nAiko: {response.text}")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nArigato senpai >_< Matane!")
            break
        except Exception as e:
            print(f"\n[Aiko encountered an error]: {e}")

if __name__ == "__main__":
    main()
