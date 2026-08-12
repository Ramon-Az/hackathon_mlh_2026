---
marp: true
theme: default
paginate: true
size: 16:9
title: "Building Agents with Google ADK"
footer: "Building Agents with Google ADK | Major League Hacking"
---

# Building Agents with Google ADK
**Facilitator:** Alberto Camarena
**Date:** 10/08/26

---

# Agenda

- Introduction & Session Objectives
- Concept Recap: Agents, Tools & Patterns
- Introduction to Google ADK (Agent Development Kit)
- Hands-on Lab: EventCraft AI Live Build
- Q&A & Wrap-Up

---

# Session Objectives

- Review the fundamental differences between LLMs and Agents
- Understand how tools and function calling enable agent capabilities
- Explore multi-agent architectures and orchestration patterns
- Gain practical experience orchestrating and registering new agents using Google ADK

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
- Ensures consistency across different architectures and environments.

---

# Single vs Multi-Agent Systems

- **Single Agent**: One massive prompt doing all tasks. Hard to scale and prone to hallucinations.
- **Multi-Agent**: Specialized sub-agents handling specific domains. Clean isolation and better accuracy.

---

# Orchestration Patterns

- **Sequential**: Agent A -> Agent B -> Agent C
- **Supervisor / Router**: A Lead agent delegates tasks to specialized sub-agents based on the user's request.
- **Hierarchical**: Multi-level trees of agents.

---

# Focus: Google ADK (Agent Development Kit)

- Built specifically for the Gemini Agent Platform.
- Provides native support for **Agents**, **Sub-Agents**, and **Function Tools**.
- Uses an **Agent Runner** to seamlessly handle multi-turn conversations and tool executions.

---

# Today's Workshop: EventCraft AI

1. Explore the Starter Code: Lead Agent, Sponsor Agent, Marketing Agent, Catering Agent.
2. **Live Build**: Code the Logistics & Venue Agent.
3. Register the new Sub-Agent with the ADK Runner.
4. Test it live in the UI!
