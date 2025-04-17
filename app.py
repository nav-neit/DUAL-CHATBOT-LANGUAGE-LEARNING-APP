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

## helper fucntion
def show_messages(mesg_1, mesg_2, message_counter, time_delay, language, batch = False, audio = False, translation = False):
    """
    Display conversation exchanges, This helper function supports displaying original texts, translated texts and audio speech.
    
    Output: 
    message_counter: updated counter for ID key
    """
    
    for i, mesg in enumerate([mesg_1, mesg_2]):
        ## show original exchange
        message(f"{mesg['content']}", is_user=i==1, avatar_style="bottts", seed = AVATAR_SEED[i], key = str(message_counter))
        message_counter +=1

        ## mimic time interval between conversations
        ## (this time delay appears when generating the conversation script for the first time)
        if not batch:
            time.sleep(time_delay)
        ## show translated message
        if translation:
            ## is user defines message should be left / right alighed
            message(f"{mesg['translation']}", is_user=i==1, avatar_style="bottts", seed=AVATAR_SEED[i], key = str(message_counter))
            message_counter +=1

        ## append the audio to the exchange
        if audio:
            ## gtts library to create audio speech in the target language based on the generated script.
            ## Library has a limitation - t can have only one voice
            tts = gTTS(text = mesg['content'], lang=AUDIO_SPEECH[language])
            sound_file = BytesIO()
            tts.write_to_fp(sound_file)
            st.audio(sound_file)
        
    return message_counter


## basic ui layout with options for user to select

# set the title at the top
st.title('Language Learning App 🌍📖🎓')

# set the description of the app
st.markdown("""
This app generates conversation or debate scripts to aid in language learning 🎯 \n
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

# Add reset button to clear session state
if st.sidebar.button("🔄 Reset Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# Define containers and columns
conversation_container = st.container()
translate_col, original_col, audio_col = st.columns(3)

## streamlit session state to store user-specific session data in the streamlit app
if "bot1_mesg" not in st.session_state:
    st.session_state["bot1_mesg"] = []
    ## this is a list whose elements are a dictionary that holds the message spoekn by first chatbot
    ## keys - role, content, translation

if "bot2_mesg" not in st.session_state:
    st.session_state["bot2_mesg"] = []
    ## same as bot1_msg

if 'batch_flag' not in st.session_state:
    st.session_state["batch_flag"] = False
    ## indicates whether the conversation messages are shown all at once or with a time delay
    ## the chat between the bots will appear with a time delay when thier conversations are generated for the first time
    ## when user wants to see the translation/add audio for the generated conv, the stored conversation messages "bot1_mesg" "bot2_mesg" can be shown at once
    ## this is benefecial since we dont need to call api again , reduces cost and latency


if 'translate_flag' not in st.session_state:
    st.session_state['translate_flag'] = False
    ## indicates if its a translation

if 'audio_flag' not in st.session_state:
    st.session_state["audio_flag"] = False
    ## indicates if its a audio

if 'message_counter' not in st.session_state:
    st.session_state["message_counter"] = 0
    ## adds one whenever a message from chatbot is displayed
    ## also to add message ID with this counter as streamlit requires that each UI components to have a unique ID                      

## streamlit reruns / reload the scripts on every user interaction
## regular python variables would lose thier values, and the app would reset to its initial state
## "session_state" in streamlit provides a way to store and retrieve data that persists throughout the user's session
## even if the app is reloaded or the user navigates between different components or pages

##Letting chatbots interact and generate conversations
if 'dual_chatbots' not in st.session_state:

    if st.sidebar.button('Generate'):
        if learning_mode == 'Conversation' and (not role1 or not action1 or not role2 or not action2 or not scenario):
            st.warning("Please fill out all role and scenario fields before generating.")
        elif learning_mode == 'Debate' and not scenario:
            st.warning("Please enter a debate topic before generating.")
        else:
            ## add flag to indicate first time script running
            st.session_state["first_time_exec"] = True

            with conversation_container:
                if learning_mode == 'Conversation':
                    st.write(f"""
                                #### The following conversation happens between {role1} and {role2} {scenario} 🎭
                            """)
                else:
                    st.write(f"""### Debate 💬 : {scenario}""")
                
                ## Instantiate dual chatbot system
                dual_chatbots = DualChatbot(engine, role_dict, language, scenario, proficiency_level, learning_mode, session_length)
                st.session_state['dual_chatbots'] = dual_chatbots

                ## start exchanges
                for _ in range(MAX_EXCHANGE_COUNTS[session_length][learning_mode]):
                    output1, output2, translate1, translate2 = dual_chatbots.step()

                    mesg_1 = {"role" : dual_chatbots.chatbots['role1']['name'],
                            "content" : output1, "translation" : translate1}
                    mesg_2 = {"role" : dual_chatbots.chatbots['role2']['name'],
                            "content" : output2, "translation" : translate2}
                    
                    new_count = show_messages(mesg_1, mesg_2, 
                                            st.session_state["message_counter"],
                                            time_delay = time_delay, language=language, batch = False,
                                            audio = False, translation = False)
                    st.session_state["message_counter"] = new_count

                    ## update session state
                    st.session_state.bot1_mesg.append(mesg_1)
                    st.session_state.bot2_mesg.append(mesg_2)

## upon running the script for first time , the two chatbots will chat back and forth given number of times and all messages get stored in session state
## show_message is a helper function designed to be the sole interface to style the message display

## when the user ineracts with the app and changes some settings, Streamlit will rerun the entire script from the top.
## But we need not invoke the LLM api again instead we retrieve the stored information

if 'dual_chatbots' in st.session_state:

    # show translation
    if translate_col.button('Translate to English'):
        st.session_state['translate_flag'] = True
        st.session_state['batch_flag'] = True
    # show original text
    if original_col.button('Show original'):
        st.session_state['translate_flag'] = False
        st.session_state['batch_flag'] = True
    # Append audio
    if audio_col.button('Play audio'):
        st.session_state['audio_flag'] = True
        st.session_state['batch_flag'] = True

    # retrieve generated conversation & chatbots
    mesg1_list = st.session_state.bot1_mesg
    mesg2_list = st.session_state.bot2_mesg
    dual_chatbots = st.session_state['dual_chatbots']

    # control message appearance
    if st.session_state['first_time_exec']:
        st.session_state['first_time_exec'] = False
    else:
        # show complete message
        with conversation_container:
            if learning_mode == 'Conversation':
                st.write(f"""### {role1} and {role2} {scenario} 🎭""")
            else:
                st.write(f"""### Debate 💬: {scenario}""")

            for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
                new_count = show_messages(mesg_1, mesg_2,
                                          st.session_state["message_counter"],
                                          time_delay = time_delay,
                                          language=language,
                                          batch = st.session_state['batch_flag'],
                                          audio = st.session_state['audio_flag'],
                                          translation = st.session_state['translate_flag']
                                          )
                st.session_state["message_counter"] = new_count

    ## Summary of key learning points in Ui
    summary_expander = st.expander('Key Learning Points')
    scripts = []
    for mesg_1, mesg_2 in zip(mesg1_list, mesg2_list):
        for i , mesg in enumerate([mesg_1, mesg_2]):
            scripts.append(mesg['role'] + ': ' + mesg['content'])

    ## compile summary
    if "summary" not in st.session_state:
        summary = dual_chatbots.summary(scripts)
        st.session_state["summary"] = summary
    else:
        summary = st.session_state["summary"]
    with summary_expander:
        st.markdown(f"**Here is the learning summary: **")
        st.write(summary)