import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { AIMessage } from '@langchain/core/messages';
import { EventState } from '../state';
import { getVenueDetailsTool } from '../tools/venue.tool';
import { getChatModel } from '../model';

export function getVenueAgent() {
  return createReactAgent({
    llm: getChatModel(),
    tools: [getVenueDetailsTool],
    stateModifier:
      'You are the Venue & Logistics Agent. Answer questions about venue capacity, room layouts, Wi-Fi, and equipment using your tools.',
  });
}

export async function venueAgentNode(state: typeof EventState.State) {
  const agent = getVenueAgent();
  const result = await agent.invoke({
    messages: state.messages,
  });

  const lastMsg = result.messages[result.messages.length - 1];
  const content =
    typeof lastMsg.content === 'string'
      ? lastMsg.content
      : JSON.stringify(lastMsg.content);

  return {
    messages: [new AIMessage({ content, name: 'VenueAgent' })],
    traces: [
      '🎪 Venue Agent (LangChain Agent): Executed React Agent workflow.',
    ],
  };
}
