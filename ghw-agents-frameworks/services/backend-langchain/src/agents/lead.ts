import { BaseMessage, HumanMessage } from '@langchain/core/messages';
import { eventGraphApp } from './graph';

interface GraphResult {
  messages?: BaseMessage[];
  traces?: string[];
}

export async function runLeadAgent(
  userMessage: string,
): Promise<{ reply: string; traces: string[]; activeAgents: string[] }> {
  try {
    const initialInput = {
      messages: [new HumanMessage(userMessage)],
      traces: ['🚀 Initializing LangGraph Event Workflow...'],
    };

    const result = (await eventGraphApp.invoke(initialInput)) as GraphResult;

    const messages = result.messages || [];
    const aiMessages = messages.filter((m: BaseMessage) => {
      const type: string = m._getType();
      return type === 'ai' || type === 'assistant';
    });
    const lastMsg =
      aiMessages.length > 0
        ? aiMessages[aiMessages.length - 1].content
        : 'Workflow completed.';

    const traces = result.traces || [];
    const activeAgents: string[] = ['lead'];

    if (traces.some((t) => t.includes('Sponsor'))) activeAgents.push('sponsor');
    if (traces.some((t) => t.includes('Marketing')))
      activeAgents.push('marketing');
    if (traces.some((t) => t.includes('Venue'))) activeAgents.push('venue');
    if (traces.some((t) => t.includes('Catering')))
      activeAgents.push('catering');

    return {
      reply: typeof lastMsg === 'string' ? lastMsg : JSON.stringify(lastMsg),
      traces,
      activeAgents,
    };
  } catch (error: unknown) {
    console.error('Error executing LangGraph workflow:', error);
    const errMsg = error instanceof Error ? error.message : String(error);
    return {
      reply: `Failed to execute LangGraph agent. (${errMsg})`,
      traces: [
        '🚀 Initializing LangGraph Event Workflow...',
        `❌ Error in LangGraph execution: ${errMsg}`,
      ],
      activeAgents: ['lead'],
    };
  }
}
