import streamlit as st
import openai

import os
from typing import Iterator

st.title('NeuroGPT')

focus_san = """
<style>
    @font-face {
        font-family: "Focussans Regular";
        src: url("../fonts/Graphik-Semibold.woff2") format("woff2");
    }

    html, body, [class*="css"]  {
		font-family: "Focussans Regular";
	}
</style>"""
st.markdown(focus_san, unsafe_allow_html=True)

openai.api_key = os.getenv('OPENAI_API_KEY')

if 'history' not in st.session_state:
    st.session_state['history'] = []

for msg in st.session_state['history']:
    st.chat_message(msg['role']).write(msg['content'])


def add_to_history(role: str, content: str) -> None:
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


placeholder = 'Hi, there! Enter what you want to let me know here.'
if prompt := st.chat_input(placeholder):
    st.chat_message('user').markdown(prompt)
    add_to_history('user', prompt)

    with st.chat_message('assistant'):
        res_box = st.empty()
        full_res = ''
        gpt_res = get_gpt_response(prompt)
        next(gpt_res)  # Remove the role entry
        for chunk in gpt_res:
            if new_info := chunk['choices'][0]['delta']:
                new_text = new_info['content']
                full_res += new_text
                res_box.markdown(full_res + ':rainbow:')
            else:
                # We hit the end of the GPT response
                res_box.markdown(full_res)

        add_to_history('assistant', full_res)
