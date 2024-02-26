import streamlit as st
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
import openai
import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer
from utils import speech_to_text, text_to_speech, autoplay_audio
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
# Initialize floating features for the interface
float_init()
# st.set_page_config(page_title="Voice-to-Voice Chatbot", page_icon="🤖", layout="centered", initial_sidebar_state="auto", menu_items=None)


# Initialize session state for managing chat messages
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Click on the below microphone to ask your queries!"}]

initialize_session_state()


openai.api_key = st.secrets.openai_key
st.title("Voice-to-Voice Chatbot 🤖")

# Load the Llama Index
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the data – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_files=["waste_managment_kb.pdf"], recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, system_prompt="You are an assistant who is expert in waste management. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

# Initialize the chat engine
if "chat_engine" not in st.session_state.keys():
    memory = ChatMemoryBuffer.from_defaults(token_limit=15000)
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", memory=memory, system_prompt="You are an expert in waste management, who performs friendly conversations with the user. If you do not find any answers to the question just say 'Please ask something related to Waste Management'", verbose=True)

# Create a container for the microphone and audio recording
with st.container():
    audio_bytes = audio_recorder(text="",recording_color="#e8b62c", icon_name="microphone", neutral_color="#6aa36f", icon_size="2x", pause_threshold=5.0)

# Create a container for chat messages with a fixed height
chat_container = st.container()
with chat_container:
    # chat_container = st.container()
    # with chat_container:
    for message in st.session_state.messages:  # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Add a scrollbar to the chat messages container
st.markdown(
    """
    <style>
    .st-bb {
        padding-top: 0;
    }
    .st-cf {
        padding-top: 0;
    }
    .stContainer > .stBlock > .stBlock > div {
        max-height: 50px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# for message in st.session_state.messages:  # Display the prior chat messages
#     with chat_container.chat_message(message["role"]):
#         st.write(message["content"])

if audio_bytes:
    with st.spinner("Transcribing..."):
        # Write the audio bytes to a temporary file
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        # Convert the audio to text using the speech_to_text function
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with chat_container.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with chat_container.chat_message("assistant"):
        response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
        st.write(response.response)
        message = {"role": "assistant", "content": response.response}
        st.session_state.messages.append(message)  # Add response to message history

        audio_file = text_to_speech(response.response)
        autoplay_audio(audio_file)
        os.remove(audio_file)

# import streamlit as st
# from llama_index.core import VectorStoreIndex, ServiceContext, Document
# from llama_index.llms.openai import OpenAI
# import openai
# import os
# from llama_index.core import SimpleDirectoryReader
# from llama_index.core.memory import ChatMemoryBuffer
# from utils import speech_to_text, text_to_speech, autoplay_audio
# from audio_recorder_streamlit import audio_recorder
# from streamlit_float import *
# # Initialize floating features for the interface
# float_init()
# # st.set_page_config(page_title="Voice-to-Voice Chatbot", page_icon="🤖", layout="centered", initial_sidebar_state="auto", menu_items=None)


# # Initialize session state for managing chat messages
# def initialize_session_state():
#     if "messages" not in st.session_state:
#         st.session_state.messages = [{"role": "assistant", "content": "Click on the below microphone to ask your queries!"}]

# initialize_session_state()


# openai.api_key = st.secrets.openai_key
# st.title("Voice-to-Voice Chatbot 🤖")

# # Load the Llama Index
# @st.cache_resource(show_spinner=False)
# def load_data():
#     with st.spinner(text="Loading and indexing the data – hang tight! This should take 1-2 minutes."):
#         reader = SimpleDirectoryReader(input_files=["waste_managment_kb.pdf"], recursive=True)
#         docs = reader.load_data()
#         service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, system_prompt="You are an assistant who is expert in waste management. Keep your answers technical and based on facts – do not hallucinate features."))
#         index = VectorStoreIndex.from_documents(docs, service_context=service_context)
#         return index

# index = load_data()

# # Initialize the chat engine
# if "chat_engine" not in st.session_state.keys():
#     memory = ChatMemoryBuffer.from_defaults(token_limit=15000)
#     st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", memory=memory, system_prompt="You are an expert in waste management, who performs friendly conversations with the user. If you do not find any answers to the question just say 'Please ask something related to Waste Management'", verbose=True)

# # Create a container for the microphone and audio recording
# footer_container = st.container()
# with footer_container:
#     audio_bytes = audio_recorder(text="",recording_color="#e8b62c", icon_name="microphone", neutral_color="#6aa36f", icon_size="2x", pause_threshold=5.0)
    
# chat_container = st.container()
# with chat_container:
#     for message in st.session_state.messages:  # Display the prior chat messages
#         with st.chat_message(message["role"]):
#             st.write(message["content"])
    
    
#     if audio_bytes:
#         with st.spinner("Transcribing..."):
#             # Write the audio bytes to a temporary file
#             webm_file_path = "temp_audio.mp3"
#             with open(webm_file_path, "wb") as f:
#                 f.write(audio_bytes)
    
#             # Convert the audio to text using the speech_to_text function
#             transcript = speech_to_text(webm_file_path)
#             if transcript:
#                 st.session_state.messages.append({"role": "user", "content": transcript})
#                 with st.chat_message("user"):
#                     st.write(transcript)
#                 os.remove(webm_file_path)

# # footer_container = st.container()
# # with footer_container:
# #     # Start the audio recorder
# #     audio_bytes = audio_recorder()

# #     # Add a button to manually stop the recording
# #     if st.button('Stop Recording'):
# #         if audio_bytes:
# #             with st.spinner("Transcribing..."):
# #                 # Write the audio bytes to a temporary file
# #                 webm_file_path = "temp_audio.mp3"
# #                 with open(webm_file_path, "wb") as f:
# #                     f.write(audio_bytes)

# #                 # Convert the audio to text using the speech_to_text function
# #                 transcript = speech_to_text(webm_file_path)
# #                 if transcript:
# #                     st.session_state.messages.append({"role": "user", "content": transcript})
# #                     with st.chat_message("user"):
# #                         st.write(transcript)
# #                     os.remove(webm_file_path)

# # If last message is not from assistant, generate a new response
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         response = st.session_state.chat_engine.chat(st.session_state.messages[-1]["content"])
#         st.write(response.response)
#         message = {"role": "assistant", "content": response.response}
#         st.session_state.messages.append(message)  # Add response to message history

#         audio_file = text_to_speech(response.response)
#         autoplay_audio(audio_file)
#         os.remove(audio_file)
# # footer_container.float("bottom: 0rem;")
