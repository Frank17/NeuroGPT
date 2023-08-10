import streamlit as st
import openai

import os
from typing import Iterator


ND_PROMPT = ('The following text is typed by an neurodiverse individual. '
             'Please reply to them in a friendly and appropriate manner. ')

openai.api_key = os.getenv('OPENAI_API_KEY')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Start defining webpage elements
st.title('NeuroGPT')

init_prompt = st.selectbox(
    'You might want to try these prompts...',
    ['How to socialize?',
     'How to focus on tasks?',
     'How to find peace in daily work?']
)
chat_room = st.container()

if 'history' not in st.session_state:
    st.session_state['history'] = []

for msg in st.session_state['history']:
    chat_room.chat_message(msg['role']).write(msg['content'])


def add_to_history(content: str, role: str) -> None:
    st.session_state['history'].append(
        {'role': role, 'content': content}
    )


def get_gpt_response(prompt: str) -> Iterator[dict]:
    return openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.5,
        stream=True
    )


instr = 'Hi there! Enter what you want to let me know here.'
with st.form('chat_input_form'):
    input_col, btn_col = st.columns([8.5, 1])

    with input_col:
        prompt = st.text_input(
            instr,
            value=init_prompt,
            placeholder=instr,
            label_visibility='collapsed'  # Hide the label
        )

    with btn_col:
        submitted = st.form_submit_button('Chat')

    if prompt and submitted:
        chat_room.chat_message('user').markdown(prompt)
        add_to_history(prompt, 'user')

        with chat_room.chat_message('assistant'):
            msg = st.empty()
            full_res = ''
            gpt_res = get_gpt_response(ND_PROMPT + prompt)
            next(gpt_res)  # Remove the role entry
            for chunk in gpt_res:
                if new_text := chunk['choices'][0]['delta']:
                    full_res += new_text['content']
                    msg.markdown(full_res + ':rainbow:')
                else:
                    # We hit the end of the GPT response
                    msg.markdown(full_res)

            add_to_history(full_res, 'assistant')
