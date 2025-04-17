from single_chat_bot import Chatbot
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("GROQ API KEY Environment variable not set")


## A Dual Chat Bot class to let two chatbots interact with each ohter
class DualChatbot:
    """
    Class definition for dual-chatbots interaction system,
    created with Langchain
    """
    
    def __init__(self, engine, role_dict, language, scenario, proficiency_level, learning_mode, session_length):
        ## Instantiate two chatbots
        self.engine = engine
        self.proficiency_level = proficiency_level
        self.language = language
        self.chatbots = role_dict
        ## self.chatbots is a dict designed to store info related to both bots
        for k in role_dict.keys():
            self.chatbots[k].update({'chatbot': Chatbot(engine)})

        ## assigning roles for two chatbots
        self.chatbots['role1']['chatbot'].instruct(
            role = self.chatbots['role1'],
            oppo_role = self.chatbots['role2'],
            language = language,
            scenario = scenario,
            session_length = session_length,
            proficiency_level = proficiency_level,
            learning_mode = learning_mode,
            starter = True
        )
        self.chatbots['role2']['chatbot'].instruct(
            role = self.chatbots['role2'],
            oppo_role = self.chatbots['role1'],
            language = language,
            scenario = scenario,
            session_length = session_length,
            proficiency_level = proficiency_level,
            learning_mode = learning_mode,
            starter = False
        )

        ## add session length
        self.session_length = session_length
        
        ## prepare conversation
        self._reset_conversation_history()

    def _reset_conversation_history(self):
        """
        serves to initiate a fresh conversation history and provide initial info to chatbots
        """
        # placeholder for conversation history
        self.conversation_history = []

        ## inputs for two chatbots
        self.input1 = "Start the conversation"
        self.input2 = ""
    
    def step(self):
        """
        Facilitates interaction between the two bots, 
        Makes one exchange round between two chatbots
        """

        ## chatbot1 speaks
        output1 = self.chatbots['role1']['chatbot'].conversation.predict(input = self.input1)
        self.conversation_history.append({"bot":self.chatbots['role1']['name'], "text" : output1})

        ## pass output of chatbot1 as input to chatbot2
        self.input2 = output1

        ## chatbot2 speaks
        output2 = self.chatbots['role2']['chatbot'].conversation.predict(input = self.input2)
        self.conversation_history.append({"bot" : self.chatbots['role2']['name'], "text": output2})

        ## pass output of chatbot2 as input to chatbot1
        self.input1 = output2

        # translate responses
        ## translate method translate the script to English
        ## helps users understand the meaning of conversation in target language
        translate1 = self.translate(output1)
        translate2 = self.translate(output2)

        return output1, output2, translate1, translate2
    
    def translate(self, message):
        """
        We employ the basic LLMChain which requires a backend LLM model and a prompt for instruction.
        This will then translate the generated script to English
        """
        if self.language == 'English':
            ## no translation performed
            translation = 'Translation : ' + message
        else:
            ## intantiate translator
            if self.engine == "GroqCloud":
                self.translator = ChatGroq(
                temperature = 0,
                api_key = api_key,
                model = "llama-3.3-70b-versatile"
                )
            else:
                raise KeyError("Currently unsupported translation model type!")
            
            ## specify instruction
            instruction = """
            Translate the following sentence from {src_lang} (source language)
            to {trg_lang} (target language).
            Here is the sentence in source language: \n
            {src_input}.
            """

            prompt = PromptTemplate(
                input_variables = ["src_lang", "trg_lang", "src_input"],
                template = instruction
            )

            ## creare a language translation chain
            translator_chain = LLMChain(llm = self.translator, prompt = prompt)
            translation = translator_chain.predict(
                src_lang = self.language,
                trg_lang = "English",
                src_input = message
                )
            
        return translation
    
    def summary(self, script):
        """
        Creates a summary of the key language learning points of the generated conversation script.
        Key vocabulary, grammar points, function phrases.
        This summary is created based on the user's proficiency level
        """

        ## instantiate a summary bot
        if self.engine == "GroqCloud":
            self.summary_bot = ChatGroq(
                temperature = 0,
                api_key = api_key,
                model = "llama-3.3-70b-versatile"
                )
        else:
            raise KeyError("Currently unsupported summary model type!")
        
        ## specify instruction
        instruction = """
        The following text is a simulated conversation in {src_lang}.
        The goal of this text  is to aid {src_lang} learners to learn real-life
        usage of {src_lang}. Therefore , your task is to summarize the key learning
        points based on the given text. Specifically, you should summarize the key vocabulary,
        grammar points and function phrases that could be important for students learning {src_lang}.
        Your summary should be conducted in English , but use examples from the text in the original language where appropriate.
        Remember your target students have proficiency level of  {proficiency} in {src_lang}. Your 
        summarization must match thier proficiency level.

        The conversation is :\n
        {script}
        """

        prompt = PromptTemplate(
            input_variables = ["src_lang", "proficiency", "script"],
            template=instruction
        )

        ## create a language summary chain
        summary_chain = LLMChain(llm = self.summary_bot, prompt = prompt)
        summary = summary_chain.predict(
            src_lang = self.language,
            proficiency = self.proficiency_level,
            script = script
        )

        return summary