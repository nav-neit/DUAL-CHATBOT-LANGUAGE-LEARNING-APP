import warnings
warnings.filterwarnings("ignore")
import streamlit as st
from streamlit_chat import message
from dual_chat_bot import DualChatbot
import time
from gtts import gTTS
from io import BytesIO

## streamlit chat library - sepcifcally designed for creating chatbot UI's
## gtts : Google Text-to-Speech, to add audio to the bot-generated conversation script in the project
## user interface using streamlit

## define the language learning settings
LANGUAGES = ['English', 'German', 'Spanish', 'French']
SESSION_LENGHTS = ['Short', 'Long']
PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']
MAX_EXCHANGE_COUNTS = {
    'Short' : {'Conversation' : 8, 'Debate' : 4},
    'Long' : {'Conversation' : 16, 'Debate': 8}
}

AUDIO_SPEECH = {
    'English' : 'en',
    'German' : 'de', 
    'Spanish' : 'es',
    'French' : 'fr'
}
# avatar seed is used for generating different avatar icons for different chatbots
AVATAR_SEED = [123, 42]

## define backbone LLM
engine = 'GroqCloud'

## basic ui layout with options for user to select

# set the title at the top
st.title('Language Learning App 🌍📖🎓')

# set the description of the app
st.markdown("""
This app generates conversation or debate scripts to aid in language learning 🎯 
Choose your desired settings and press 'Generate to start'  🚀
"""
)

# Add a selection for learning mode
learning_mode = st.sidebar.selectbox('Learning Mode 📖',('Conversation', 'Debate'))

if learning_mode == 'Conversation':
    role1 = st.sidebar.text_input('Role 1 🎭')
    action1 = st.sidebar.text_input('Action 1 🗣️')
    role2 = st.sidebar.text_input('Role 2 🎭')
    action2 = st.sidebar.text_input('Action 2 🗣️')
    scenario = st.sidebar.text_input('Scenario 🎥')
    time_delay = 2

    # configiure role dictionary
    role_dict = {
        'role1' : {'name': role1, 'action' : action1},
        'role2' : {'name': role2, 'action' : action2}
    }
else:
    scenario = st.sidebar.text_input('Debate Topic 💬')

    # configure role dictionary
    role_dict = {
        'role1' : {'name' : 'Proponent'},
        'role2' : {'name' : 'Opponent'}
    }
    time_delay = 5

language = st.sidebar.selectbox('Target Language 🔤', LANGUAGES)
session_length = st.sidebar.selectbox('Session Length ⏰', SESSION_LENGHTS)
proficiency_level = st.sidebar.selectbox('Proficiency Level 🏆', PROFICIENCY_LEVELS)

## here time_delay is used for specifying the waiting time btw displaying two consecutive messages
## beneficial for user to allow enough time to read the generatred messages before the next exhange appears