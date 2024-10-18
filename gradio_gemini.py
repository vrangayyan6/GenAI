'''
gradio https://github.com/gradio-app/gradio

Used prompt below with Claude.ai
Act as an expert programmer, build chatbot using Gradio https://github.com/gradio-app/gradio, google.generativeai package, gemini-1.5-flash model

'''
import gradio as gr
import google.generativeai as genai
import os

# Set up the Gemini API
#os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the Gemini 1.5 Flash model
model = genai.GenerativeModel('gemini-1.5-flash')

def chat_with_gemini(message, history):
    # Prepare the conversation history
    # messages = [{"role": "user" if i % 2 == 0 else "model", "parts": [msg]} for i, msg in enumerate(history)]

    messages = [{"role": "user" if j % 2 == 0 else "model", "parts": msg[j]} for i, msg in enumerate(history) for j in range(len(msg))]
        
    messages.append({"role": "user", "parts": message})
    print("messages: ", messages)
    
    # Generate a response
    response = model.generate_content(messages)
    return response.text

# Create the Gradio interface
iface = gr.ChatInterface(
    fn=chat_with_gemini,
    title="Gemini 1.5 Flash Chatbot",
    description="Chat with the Gemini 1.5 Flash model using Gradio!",
    examples=["Tell me a joke", "Explain quantum computing", "Self-ask technique: I want you to answer my questions by performing a series of steps involving asking sub-questions as you proceed to derive a final answer. You are to identify relevant sub-questions one at a time, answer each such sub-question one at a time, and then use those series of answers to reach a final overall answer. Do you understand these instructions on how I want you to solve problems?"],
    #retry_btn="Regenerate",
    #undo_btn="Undo",
    #clear_btn="Clear",
)

# Launch the interface
iface.launch()
