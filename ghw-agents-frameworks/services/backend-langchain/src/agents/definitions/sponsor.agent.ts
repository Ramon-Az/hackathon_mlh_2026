import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { AIMessage } from '@langchain/core/messages';
import { EventState } from '../state';
import { getSponsorshipPackagesTool } from '../tools/sponsorship.tool';
import { getChatModel } from '../model';

export function getSponsorAgent() {
  return createReactAgent({
    llm: getChatModel(),
    tools: [getSponsorshipPackagesTool],
    stateModifier:
      'You are the Sponsorship Agent. Help users calculate tier pricing, perks, and sponsor benefits using your tools.',
  });
}

export async function sponsorAgentNode(state: typeof EventState.State) {
  const agent = getSponsorAgent();
  const result = await agent.invoke({
    messages: state.messages,
  });

  const lastMsg = result.messages[result.messages.length - 1];
  const content =
    typeof lastMsg.content === 'string'
      ? lastMsg.content
      : JSON.stringify(lastMsg.content);

  return {
    messages: [new AIMessage({ content, name: 'SponsorAgent' })],
    traces: [
      '💼 Sponsor Agent (LangChain Agent): Executed React Agent workflow.',
    ],
  };
}
