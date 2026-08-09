# 🤖 Building Smarter AI Agents with Google Gemini

A beginner-friendly project built during **MLH Global Hack Week: Agents**.

In this workshop, we use **Node.js** and **Google Gemini** to build increasingly capable AI agents — from a simple Gemini request to conversation memory, vision, and tool calling.

## 🚀 What You'll Learn

- Connect Node.js to the Gemini API
- Build an interactive Gemini chat agent
- Give an agent conversation memory
- Use Gemini's multimodal capabilities to understand images
- Give Gemini tools and let it decide when to use them
- Understand how function/tool calling works

## 🛠️ Getting Started

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd ghw-agents-gemini
```

Install dependencies:

```bash
npm install
```

Create your `.env` file:

```bash
cp .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

You can create an API key using [Google AI Studio](https://aistudio.google.com/).

> ⚠️ Never commit your `.env` file or API key to GitHub.

## 🧪 Workshop Steps

### Step 1 — Meet Gemini

Make your first request to the Gemini API.

```bash
node step-1-gemini.js
```

### Step 2 — Chat Agent + Memory

Turn Gemini into an interactive terminal agent that remembers the current conversation.

```bash
node step-2-chat-agent.js
```

### Step 3 — Give Your Agent Eyes 👀

Send an image to Gemini and let the agent understand and reason about what it sees.

Add your image as `demo-image.jpg`, then run:

```bash
node step-3-vision-agent.js
```

### Step 4 — Give Your Agent Tools 🔧

Give Gemini access to a JavaScript weather tool and let the model decide when the tool is needed.

```bash
node step-4-tool-agent.js
```

Try:

```text
What is JavaScript?
```

Then:

```text
What's the weather in Lagos?
```

Notice that Gemini can answer the first question directly but decides to use our weather tool for the second.

## 🧠 How Tool Calling Works

```text
User
  ↓
Gemini
  ↓
Decides a tool is needed
  ↓
Requests getWeather("Lagos")
  ↓
Our Node.js app runs the function
  ↓
Tool result
  ↓
Gemini
  ↓
Final answer
```

Gemini decides **which tool to request and what arguments to provide**, while our application actually executes the JavaScript function.

## 💡 Challenge

Take what we built and make the agent smarter!

Try:

- Adding a calculator tool
- Connecting a real weather API
- Adding another image use case
- Creating multiple tools
- Combining memory + vision + tools

## 🌎 MLH Global Hack Week

**Session:** Building Smarter AI Agents with Google Gemini

**Check-in:** https://events.mlh.com/events/14591-ghw-agents-week-building-smarter-ai-agents-with-google-gemini

**Feedback:** https://mlh.link/GHWFeedback

Happy building! 🚀