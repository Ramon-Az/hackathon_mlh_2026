# 🤖 Build Your First AI Agent with OpenAI

A beginner-friendly project built during **MLH Global Hack Week: Agents**.

In this workshop, we build a simple AI agent using **Node.js** and the **OpenAI API**, then make it interactive and give it temporary conversation memory.

## 📚 What You'll Learn

- Connect a Node.js application to the OpenAI API
- Build an interactive AI agent
- Give your agent instructions (personality)
- Add temporary conversation memory
- Understand the core building blocks of an AI agent

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/vincentiroleh/ghw-agents-day1.git
cd ghw-agents-day1
```

Install dependencies:

```bash
npm install
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

> **Never commit your `.env` file or API key to GitHub.**

## ▶️ Run the Examples

### Step 1 – First OpenAI Request

```bash
node step-1-first-request.js
```

### Step 2 – Interactive AI Agent

```bash
node step-2-interactive-agent.js
```

### Step 3 – AI Agent with Memory

```bash
node step-3-agent-with-memory.js
```

Or, if you're using the npm scripts:

```bash
npm run step1
npm run step2
npm run step3
```

## 🧠 What Makes This an AI Agent?

A simple AI agent consists of:

- 🧠 **Brain** – The LLM (OpenAI)
- 📋 **Instructions** – How the agent should behave
- 📝 **Memory** – Conversation history

## 💡 Challenge

Take `step-3-agent-with-memory.js` and customize the `instructions` to create your own AI agent.

Ideas:

- 👨‍💻 Coding Mentor
- 📚 Study Buddy
- 💼 Career Coach
- ✈️ Travel Planner
- 🤖 Personal Assistant

## 🔗 MLH Global Hack Week

**Session:** Build Your First AI Agent with OpenAI (Beginner Friendly)

Check-in: https://events.mlh.com/events/14585

Happy building! 🚀
