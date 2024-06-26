import os
import json
import pandas as pd
import traceback
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks import get_openai_callback
from src.mcqgenerator.mcqgenerator import genrate_evaluation_chain
from src.mcqgenerator.logger import logging

#Loading the json file
with open("response.json", "r") as f:
    RESPONSE_JSON = json.load(f)


#Creating a title of the app
st.title("MCQs Creator Application with LangChain")

with st.form("User Input"):
    uploaded_file = st.file_uploader("Upload pdf or text file")
    mcq_count = st.number_input("no of mcq's", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity Level of question", max_chars=20, placeholder="Simple")

    # Every form must have a submit button.
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                #counts tokens and the cost of API call
                with get_openai_callback() as cb:
                    response = genrate_evaluation_chain(
                        {
                            "text":text,
                            "number": mcq_count,
                            "subject":subject,
                            "tone":tone,
                            "response_json":json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")
            
            else:
                print(f"Total tokens:{cb.total_tokens}")
                print(f"Prompt tokens:{cb.prompt_tokens}")
                print(f"Completion tokens:{cb.completion_tokens}")
                print(f"Total cost:{cb.total_cost}")

                if isinstance(response, dict):
                    #Extract the quiz data from the response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # Display the review in a text box as well
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.write(response)


