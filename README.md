# Autonomous_Requirements_and_Story-Generator
Built a stateful multi-agent agentic AI system using LangGraph that autonomously converts product briefs into user stories, acceptance criteria, and Gherkin test cases. Implemented RAG with FAISS and sentence-transformers for cross-run duplicate prevention, Chain-of-Thought and Few-Shot prompting for structured LLM output, a self-correction loop via conditional graph routing, and a non-blocking Human-in-the-Loop approval gate exposed as a REST API

# Setup & Installation
1. Clone the repository
bashgit clone https://github.com/pranju20/Autonomous_Requirements_and_Story-Generator.git
cd Autonomous_Requirements_and_Story-Generator
2. Create a virtual environment bash
  # python -m venv venv

Windows
# venv\Scripts\activate

3. Install dependencies
bashpip install -r requirements.txt
4. Configure environment variables
bashcp .env.example .env
Open .env and add your HuggingFace token:
envHF_TOKEN=your_huggingface_token_here

Get your free token at huggingface.co/settings/tokens

5. Run the server
bashuvicorn api.main:app --reload --host 0.0.0.0 --port 8000
# API Usage
Swagger UI
Open http://127.0.0.1:8000/docs for the interactive API explorer.

<img width="1714" height="823" alt="image" src="https://github.com/user-attachments/assets/b8c70c66-3577-4622-aed3-cf7d90cca553" />
<img width="1919" height="920" alt="image" src="https://github.com/user-attachments/assets/958afca5-ea71-4970-8c73-7060ba44a2d3" />
<img width="1796" height="892" alt="image" src="https://github.com/user-attachments/assets/cec8944c-481e-4cfe-aa9e-d4c1ad07e654" />
<img width="1919" height="827" alt="image" src="https://github.com/user-attachments/assets/01cc06a8-66d0-47f2-be2e-1559e50d04dd" />
<img width="1915" height="897" alt="image" src="https://github.com/user-attachments/assets/17afe2d1-c835-452d-9995-84bea73356a6" />





