'''
openai-gradio   https://github.com/gradio-app/openai-gradio/

Create OpenAI API keys https://platform.openai.com/api-keys 
Openai API models and pricing https://openai.com/api/pricing/ 

'''
import gradio as gr
import openai_gradio

gr.load(
    name='gpt-4o-mini',   # select model as needed
    src=openai_gradio.registry,
    title='OpenAI-Gradio Integration',
    description="Chat with GPT-4o-mini model.",
    examples=["Self-ask technique: I want you to answer my questions by performing a series of steps involving asking sub-questions as you proceed to derive a final answer. You are to identify relevant sub-questions one at a time, answer each such sub-question one at a time, and then use those series of answers to reach a final overall answer. Do you understand these instructions on how I want you to solve problems?", "Explain quantum gravity to a 5-year old.", "How many R are there in the word Strawberry?"]
).launch()
