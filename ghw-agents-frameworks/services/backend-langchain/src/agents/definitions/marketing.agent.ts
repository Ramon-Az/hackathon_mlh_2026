import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { AIMessage } from '@langchain/core/messages';
import { EventState } from '../state';
import { generateMarketingPostTool } from '../tools/marketing.tool';
import { getChatModel } from '../model';

export function getMarketingAgent() {
  return createReactAgent({
    llm: getChatModel(),
    tools: [generateMarketingPostTool],
    stateModifier:
      'You are the Marketing Agent. Help draft promotional social media posts using your tools.',
  });
}

export async function marketingAgentNode(state: typeof EventState.State) {
  const agent = getMarketingAgent();
  const result = await agent.invoke({
    messages: state.messages,
  });

  const lastMsg = result.messages[result.messages.length - 1];
  const content =
    typeof lastMsg.content === 'string'
      ? lastMsg.content
      : JSON.stringify(lastMsg.content);

  return {
    messages: [new AIMessage({ content, name: 'MarketingAgent' })],
    traces: [
      '📢 Marketing Agent (LangChain Agent): Executed React Agent workflow.',
    ],
  };
}
