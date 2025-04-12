## import necessary libraries
import os
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("GROQ API KEY Environment variable not set")

## we will first define a single chat bot class which can be later integrated into a dual-chatbot class
## this chat bot class enable the management of an individual chatbot with user-specified LLM as its backbone
## instructions are based on users intent, and facilitating interactive multi round conversations

class Chatbot:
    """
    class definition for a single chatbot with memory, created with LangChain
    """
    def __init__(self, engine):
        """
        select backbone LLM, as well as instantiate the memory for creating Language Chain in LangChain
        """
        
        ## instantiate LLM
        if engine == "GroqCloud":
            self.llm = ChatGroq(
                temperature = 0,
                api_key = api_key,
                model = "llama-3.3-70b-versatile"
            )
        else:
            raise KeyError("Currently unsupported chat model type")
        
        ## instantiate memory
        ## This will track the conversation history
        ## This will prepends the last few inputs/outputs to the current input of the chat bot
        self.memory = ConversationBufferMemory(return_messages=True)

    def instruct(self, role, oppo_role, language, scenario, session_length, proficiency_level, learning_mode, starter = False):
        """
        This method allows us to give instructions to the chat bot and make conversations with it.
        This sets the context of chatbot interaction
        """
        ## define language settings
        self.role = role
        self.oppo_role = oppo_role
        ## role and oppo_role are dictionaries records the role name and corresponding actions for current role and oppo roles 
        self.language = language
        ## scenario sets the stage for conversation in learning mode / debating topic in debate mode
        self.scenario = scenario
        self.session_length = session_length
        self.proficiency_level = proficiency_level
        self.learning_mode = learning_mode
        ## just a flag to indicate if the currrent chat bot will initiate the conversation
        self.starter = starter

        ## define prompt template
        prompt = ChatPromptTemplate.from_messages([
          ## system message controls the chatbot behavior
          SystemMessagePromptTemplate.from_template(self._specify_system_message()),
          MessagesPlaceholder(variable_name = "history"),
          HumanMessagePromptTemplate.from_template("{input}")
        ])

        ## create conversation chain
        self.conversation = ConversationChain(memory = self.memory, prompt = prompt, llm = self.llm, verbose = False)

    def _specify_system_message(self):
        """
        we guide the chatbot in participating in the conversation as desired by the user
        we have to specify the behavior of the chatbot , which consists of the following aspects:

        - general context : conducting conversation / debate under given scenario
        - the language spoken
        - purpose of simulated conversation / debate
        - language complexity requirement
        - exchange length requirement
        - other nuance constraints

        Outputs:
        ------------
        prompt : instructions for chatbot

        This method compiles a string which will then be fed into the SystemMessagePromptTemplate.from_template()
        to instruct the chat bot
        This method basically is used for a custom prompt design
        """
        ## we specify each language learning requirements
        
        ## Session Length
        ## directly specify the maximum number of exchanges that can happen in one session
        ## numbers are hardcoded for time being
        exchange_counts_dict = {
            'Short' : {'Conversation':8, 'Debate' : 4},
            'Long' : {'Conversation':16, 'Debate': 8}
        }
        exchange_counts = exchange_counts_dict[self.session_length][self.learning_mode]

        ## Speech Length
        ## Restrict how much a chat bot can say within one exchange or equivalently the number of messages
        ## for conversation mode - "no need to restrict", for debate mode - "we need to impose a limit"
        ## hardcoded numbers wrt to users proficiency level in the target language
        argument_num_dict = {
            'Beginner' : 4,
            'Intermediate' : 6,
            'Advanced' : 8
        }

        ## Speech Complexity

        if self.proficiency_level == "Beginner":
            lang_requirement = """
            use a basic and simple vocabulary and sentence structures as possible.
            Must avoid idioms, slang and complex grammatical constructs.
            """
        elif self.proficiency_level == "Intermediate":
            lang_requirement = """
            use a wider range of vocabulary and variety of structures.
            You can include some idioms and colloquial expressions,
            but avoid highly technical language or complex literary expressions.
            """
        elif self.proficiency_level == "Advanced":
            lang_requirement = """
            use sophisticated vocabulary , complex sentence structures , idoms, colloquial expressions,
            and technical language where appropriate.                        
            """
        else:
            raise KeyError("Currently unsupported proficiency level!")
        
        ## Compile Bot Instructions
        if self.learning_mode == "Conversation":
            prompt = f"""
            You are an AI that is good at role-playing.
            You are simulating a typical conversation happened {self.scenario}.
            In this scenario, you are playing as a {self.role['name']} {self.role['action']}, speaking to a 
            {self.oppo_role['name']} {self.oppo_role['action']}.
            Your conversation should only be conducted in {self.language}. Do not translate.
            This simulated {self.learning_mode} is designed for {self.language} language learners to learn real-life
            conversations in {self.language}. You should assume the learner's proficiency level in
            {self.language} is {self.proficiency_level}. Therefore , you should {lang_requirement}.
            You should finish the conversation within {exchange_counts} exchanges with the {self.oppo_role['name']}.
            Make your conversation with {self.oppo_role['name']} natural and typical in the considered scenario in
            {self.language} cultural.
            """
        elif self.learning_mode == 'Debate':
            prompt = f"""
            You are an AI that is good at debating. 
            You are now engaged in a debate with the following topic: {self.scenario}. 
            In this debate, you are taking on the role of a {self.role['name']}. 
            Always remember your stances in the debate.
            Your debate should only be conducted in {self.language}. Do not translate.
            This simulated debate is designed for {self.language} language learners to learn {self.language}. 
            You should assume the learners' proficiency level in {self.language} is {self.proficiency_level}. 
            Therefore, you should {lang_requirement}.
            You will exchange opinions with another AI (who plays the {self.oppo_role['name']} role) {exchange_counts} times. 
            Everytime you speak, you can only speak no more than {argument_num_dict[self.proficiency_level]} sentences.
            """
        else:
            raise KeyError("Currently unsupported learning mode!")


        ## instruct the chatbot whether it should speak first or wait for the response from opponsent AI:
        if self.starter:
            ## current bot is first to speak
            prompt += f"You are leading the {self.learning_mode}.\n"
        else:
            ## current bot is second one to speak
            prompt += f"Wait for the {self.oppo_role['name']}'s statement"
