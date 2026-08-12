import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { AIMessage } from '@langchain/core/messages';
import { EventState } from '../state';
import {
  getCateringPackagesTool,
  getCateringEstimateTool,
} from '../tools/catering.tool';
import { getChatModel } from '../model';

export function getCateringAgent() {
  return createReactAgent({
    llm: getChatModel(),
    tools: [getCateringPackagesTool, getCateringEstimateTool],
    stateModifier:
      'You are the Catering Agent. Help users calculate catering packages, menu options, and pricing using your tools.',
  });
}

export async function cateringAgentNode(state: typeof EventState.State) {
  const agent = getCateringAgent();
  const result = await agent.invoke({
    messages: state.messages,
  });

  const lastMsg = result.messages[result.messages.length - 1];
  const content =
    typeof lastMsg.content === 'string'
      ? lastMsg.content
      : JSON.stringify(lastMsg.content);

  return {
    messages: [new AIMessage({ content, name: 'CateringAgent' })],
    traces: [
      '🍽️ Catering Agent (LangChain Agent): Executed React Agent workflow.',
    ],
  };
}
