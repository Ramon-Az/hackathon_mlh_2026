---
marp: true
theme: default
paginate: true
size: 16:9
title: "Building Agents with LangChain"
footer: "Building Agents with LangChain | Major League Hacking"
---

# Building Agents with LangChain
**Facilitator:** Alberto Camarena
**Date:** 10/08/26

---

# Agenda

- Introduction & Session Objectives
- Concept Recap: Agents, Tools & Patterns
- Introduction to LangChain & LangGraph
- Hands-on Lab: EventCraft AI Live Build
- Q&A & Wrap-Up

---

# Session Objectives

- Understand the shift from simple LLMs to autonomous AI Agents
- Learn how tools and function calling enable agent actions
- Explore multi-agent architectures and orchestration
- Gain practical experience building and extending an agent workflow using LangChain/LangGraph

---

# What is an Agent?

**LLM vs Agent**
- **LLM**: A stateless model that takes a prompt and returns text.
- **Agent**: An autonomous system powered by an LLM that uses **Tools**, **Memory**, and a **Reasoning Loop** to accomplish goals.

---

# The Reasoning Loop

The **ReAct** (Reasoning + Acting) pattern:
1. **Thought**: What do I need to do next?
2. **Action**: Call a tool.
3. **Observation**: See the tool's output.
4. **Final Answer**: Synthesize the result.

---

# Tools & Function Calling

- We give the LLM definitions of our functions (name, description, parameters).
- The LLM returns a structured JSON calling that function instead of plain text.
- Our framework executes the function and passes the result back to the LLM.

---

# Model Context Protocol (MCP)

- A standardized way to define context and tool interfaces across applications.
- Ensures consistency whether you are in LangChain, ADK, or raw API calls.

---

# Single vs Multi-Agent Systems

- **Single Agent**: One big prompt trying to do everything (prone to distraction and context limits).
- **Multi-Agent**: Specialized agents with focused prompts and tools (easier to test, maintain, and scale).

---

# Orchestration Patterns

- **Sequential**: Agent A -> Agent B -> Agent C
- **Supervisor / Router**: A Lead agent delegates tasks to specialized sub-agents based on the user's request.
- **Hierarchical**: Multi-level trees of agents.

---

# LangChain: The Foundation Framework

- **Model Abstractions**: Standardized interfaces across Gemini, Claude, OpenAI (`ChatGoogleGenerativeAI`).
- **Tools & Structured Output**: Define tools with Zod schemas and enforce JSON responses (`tool()`, `withStructuredOutput()`).
- **Agent Primitives**: Out-of-the-box agent loops (`createAgent` / `createReactAgent`).

---

# LangGraph: Stateful Multi-Agent Engine

- **Graph Runtime**: Define complex, cyclic workflows using **Nodes** (agents/tools), **Edges**, and **State Annotations**.
- **Persistence & Memory**: Built-in checkpointers (`MemorySaver`) for multi-turn thread memory.
- **Human-in-the-Loop**: Pause execution for human review and approval.
- **Multi-Agent Teams**: Native support for Supervisor, Router, and Hierarchical agent graphs.

---

# LangChain + LangGraph: Better Together

- **LangChain** provides the *Building Blocks*: Models, Prompt Templates, Tools, and Parsers.
- **LangGraph** provides the *Control Flow*: State management, loops, conditional routing, and agent collaboration.
- **Together**: Build modular, production-ready agent teams with full observability and control.

---

# Today's Focus: EventCraft AI with LangChain & LangGraph

- **Nodes**: Lead Supervisor, Sponsor Agent, Marketing Agent, Venue Agent.
- **Edges**: Conditional routing based on user intent.
- **State**: Shared conversation message history (`EventState`).


---

# Today's Workshop: EventCraft AI

1. Explore the Starter Code: Lead Agent, Sponsor Agent, Marketing Agent.
2. **Live Build**: Code the Catering Agent / Food Tool.
3. Inject the new Agent into the LangGraph state.
4. Test it live in the UI!
