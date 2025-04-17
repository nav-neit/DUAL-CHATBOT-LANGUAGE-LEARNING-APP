# 🧠🌍 Dual Chatbot Language Learning App

An interactive Streamlit web app that simulates intelligent, real-time conversations between two AI chatbots to help you **practice and learn foreign languages**. You choose the language, roles, context, and proficiency level — the bots do the talking.

---

## 📸 Demo Screenshots

| Conversation Mode | Summary Output |
|-------------------|----------------|
| ![Chat UI](screenshots/chat_ui.jpg) | ![Summary UI](screenshots/summary_ui.jpg) |


---

## 📚 Features

- 🤖 **Dual Chatbot Interaction**: Simulates realistic dialogues between AI characters.
- 🌐 **Language Support**: English, German, Spanish, and French.
- 🎭 **Custom Role Scenarios**: Define your own characters, actions, and scene.
- 🧑‍🏫 **Learning Modes**: Choose between role-based conversation or topic-based debate.
- 🧠 **AI-Level Matching**: Customize based on Beginner, Intermediate, or Advanced learners.
- 🔊 **Text-to-Speech**: Listen to bot responses in the target language.
- 🔄 **English Translation**: View original and translated responses.
- 📝 **Smart Summary**: Get a language-learning oriented summary of key grammar, vocabulary, and phrases.

---

## 🛠 Setup Instructions

### 📥 1. Clone the Repository

```bash
git clone https://github.com/your-username/dual-chatbot-language-app.git
cd dual-chatbot-language-app

### 📥 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

### 📥 3. Install Dependencies
```bash
pip install -r requirements.txt

### 📥 4. Set Up Environment Variables
```bash
create a .env file in the root directory and add your Groq API key:
GROQ_API_KEY=your-groq-api-key-here
You can get a free key from https://console.groq.com


