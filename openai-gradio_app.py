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
).launch()
