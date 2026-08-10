# 🌍 Build an AI Agent that Uses Real APIs

A beginner-friendly project built during **MLH Global Hack Week: Agents**.

In this workshop, we connect a Groq-powered AI agent to real APIs using Node.js.

We start with a basic API request, turn it into a reusable tool, then build a smart travel agent that can choose between multiple APIs and keep working until it has enough information to answer.

## 🚀 What You'll Learn

- How REST APIs work
- How to use `fetch()` in Node.js
- How JSON API responses work
- How to turn an API into an AI agent tool
- How Groq chooses which tool to use
- How agents can use multiple real APIs
- How an agent loop works

## 🛠️ Setup

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd ghw-agents-real-apis
```

Install dependencies:

```bash
npm install
```

Create your `.env` file:

```bash
cp .env.example .env
```

Add your Groq API key (get one free at https://console.groq.com):

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> Never commit your `.env` file or API key to GitHub.

## 🧪 Workshop Steps

### Step 1 — Call a Real API

```bash
npm run step1
```

Call a weather API directly from Node.js.

### Step 2 — Turn the API into a Tool

```bash
npm run step2
```

Create a reusable `getWeather(city)` function using real geocoding and weather APIs.

### Step 3 — Let Groq Use a Real API

```bash
npm run step3
```

Groq decides when it needs the weather tool, and our Node.js application executes the real API request.

### Step 4 — Smart Travel Agent

```bash
npm run step4
```

Give Groq access to multiple real tools:

- 🌦️ Weather
- 🌍 Country information
- 💱 Currency conversion

The agent can keep using tools until it has enough information to answer.

## 🧠 Agent Loop

```text
User
 ↓
Groq
 ↓
Need a tool?
 ↓
Real API
 ↓
Tool result
 ↓
Groq thinks again
 ↓
Another tool if needed
 ↓
Final answer
```

## 💡 Try This

```text
I'm visiting Japan tomorrow.

Tell me:
- the capital
- the currency
- today's weather in the capital
- how much 300 USD is worth in their currency

Give me a short travel briefing.
```

## 🚀 Challenge

Add another real API to the agent.

Ideas:

- GitHub
- Movies
- Books
- Sports
- News
- Search
- Maps

## 🌎 MLH Global Hack Week

**Session:** Build an AI Agent that Uses Real APIs

**Check-in:** https://events.mlh.com/events/14593

**Feedback:** https://mlh.link/GHWFeedback

Happy building! 🚀