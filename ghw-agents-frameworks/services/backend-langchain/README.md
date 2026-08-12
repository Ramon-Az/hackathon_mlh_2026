# EventCraft AI - LangChain Service (Session 1)

This service powers the **Session 1** workshop backend using **LangChain** (`@langchain/core`) and **LangGraph** (`@langchain/langgraph`) paired with Google Gemini (`@langchain/google-genai`).

---

## 🏛️ Agents & Architecture Flow

The system follows a **Supervisor / Router Orchestration Pattern** managed by a central LangGraph `StateGraph`.

```text
               +-----------------------+
               |     START (User)      |
               +-----------+-----------+
                           |
                           v
               +-----------+-----------+
               |    Supervisor Node    |
               | (Event Lead Router)   |
               +----+------+------+----+
                    |      |      |
         +----------+      |      +----------+
         |                 |                 |
         v                 v                 v
+--------+-------+ +-------+--------+ +------+--------+
| Sponsor Agent  | | Marketing Agent| |  Venue Agent  |
|  (Tier Tool)   | |  (Post Tool)   | | (Details Tool)|
+--------+-------+ +-------+--------+ +------+--------+
         |                 |                 |
         +----------+      |      +----------+
                    |      |      |
                    v      v      v
               +----+------+------+----+
               |    Supervisor Node    |
               +-----------+-----------+
                           |
                           v (When FINISH)
               +-----------+-----------+
               |          END          |
               +-----------------------+
```

---

## 👥 Agent Definitions & Directory Structure

Each agent has its own dedicated file located in `src/agents/definitions/`:

1. 👑 **Supervisor Agent (`src/agents/definitions/supervisor.agent.ts`)**:
   - **Role**: Event Lead Supervisor.
   - **Mechanism**: Evaluates conversation history using `.withStructuredOutput()` to decide which specialist agent should handle the user request next, or outputs `FINISH` when complete.

2. 💼 **Sponsorship Agent (`src/agents/definitions/sponsor.agent.ts`)**:
   - **Role**: Manages corporate sponsor packages and perk tiers.
   - **Tool**: `getSponsorshipPackagesTool` (`src/agents/tools/sponsorship.tool.ts`) - Calculates package pricing and benefits for Gold ($5,000), Silver ($2,500), and Bronze ($1,000) tiers.

3. 📢 **Marketing Agent (`src/agents/definitions/marketing.agent.ts`)**:
   - **Role**: Handles promotional social media content.
   - **Tool**: `generateMarketingPostTool` (`src/agents/tools/marketing.tool.ts`) - Drafts promotional announcements tailored for Twitter/X, LinkedIn, and Instagram.

4. 🎪 **Venue Agent (`src/agents/definitions/venue.agent.ts`)**:
   - **Role**: Manages facility specs, room capacities, and equipment.
   - **Tool**: `getVenueDetailsTool` (`src/agents/tools/venue.tool.ts`) - Returns capacity, stage setup, Wi-Fi specs, and room layouts.

---

## 🍕 Session 1 Live Workshop Challenge: Catering Agent

In this workshop session, **the Catering (Food) Agent is intentionally omitted**!

### Your Mission:
1. Create `src/agents/tools/catering.tool.ts`: Implement `getCateringMenuTool` to return meal options, dietary restriction breakdown (vegan, GF, halal), and budget estimates.
2. Create `src/agents/definitions/catering.agent.ts`: Define `cateringAgentNode` bound with your catering tool.
3. Update `src/agents/definitions/supervisor.agent.ts`: Add `"CateringAgent"` to the supervisor routing options and instructions.
4. Update `src/agents/graph.ts`: Register `.addNode("CateringAgent", cateringAgentNode)` and wire its edges to `supervisor`.

---

## 🚀 Usage & API Endpoints

### 1. Environment Setup
Copy `.env.example` to `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 2. Run the Service
```bash
npm install
npm run start:dev
```
The NestJS backend will start on **http://localhost:4000**.

### 3. API Contract
* **`POST /api/chat`**
  - **Body**: `{ "message": "What perks come with the Gold sponsorship tier?" }`
  - **Response**: 
    ```json
    {
      "reply": "Gold Tier ($5,000) includes Main Stage branding, 5 VIP tickets...",
      "traces": [
        "🚀 Initializing LangGraph Event Workflow...",
        "👑 Supervisor [LangGraph]: Routing decision -> SponsorAgent",
        "💼 Sponsor Agent: Executed tool 'get_sponsorship_packages'..."
      ],
      "framework": "LangChain"
    }
    ```

