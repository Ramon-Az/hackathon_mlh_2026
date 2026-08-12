# EventCraft AI: Agent Workshop

Welcome to the **EventCraft AI** workshop repository! In this workshop, you will learn how to build AI agents to create a full Event Organizing System. 

We will compare two popular frameworks across two sessions:
- **Session 1**: Building Agents with LangChain (`@langchain/langgraph`)
- **Session 2**: Building Agents with ADK (`@google/adk`)

## 🏗️ Architecture

- **`frontend/`**: A shared React application running on port 3000 that connects to our backend services.
- **`services/backend-langchain/`**: A NestJS standalone backend for Session 1, running on port 4000.
- **`services/backend-adk/`**: A NestJS standalone backend for Session 2, running on port 4001.

*Note: You only need to run the backend for the current session along with the frontend!*

## 📚 Workshop Structure

### Session 1: Building Agents with LangChain
We will build a multi-agent system where a Lead Agent routes requests to a Sponsor Agent and a Marketing Agent. 
**Live Coding Challenge**: We will implement the Catering Agent and inject it into the LangGraph state.

### Session 2: Building Agents with ADK
We will use Google's Agent Development Kit to build a hierarchical multi-agent system.
**Live Coding Challenge**: We will build and register a Logistics & Venue Agent into the ADK Runner.

## 🚀 Setup Instructions

1. Obtain a Gemini API Key from Google AI Studio.
2. For the session you are taking, copy the `.env.example` to `.env` in the respective backend directory and add your key.
3. Install dependencies in the `frontend` and the respective `services/backend-...` folder using `npm install`.
4. Run the frontend: `npm run dev`
5. Run the backend: `npm run start:dev`

Enjoy building your agentic Event Organizers!
