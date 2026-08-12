import { SystemMessage, AIMessage } from '@langchain/core/messages';
import { z } from 'zod';
import { EventState } from '../state';
import { getChatModel } from '../model';

const members = [
  'SponsorAgent',
  'MarketingAgent',
  'VenueAgent',
  'CateringAgent',
] as const;

const routingSchema = z.object({
  next: z
    .enum(['FINISH', ...members])
    .describe(
      'Which agent to route to next, or FINISH if the user query is resolved.',
    ),
  reasoning: z.string().describe('Brief justification for routing decision.'),
});

export async function supervisorNode(state: typeof EventState.State) {
  const messages = state.messages;
  const lastMessage = messages[messages.length - 1];

  // If the last message is an AI message from a specialist sub-agent, task is finished!
  if (
    lastMessage &&
    (lastMessage._getType() === 'ai' || lastMessage._getType() === 'assistant')
  ) {
    const sender = (lastMessage as AIMessage).name || 'Specialist Agent';
    return {
      next: 'FINISH',
      traces: [
        `👑 Supervisor [LangGraph]: Task completed by ${sender}. Routing decision -> FINISH`,
      ],
    };
  }

  const model = getChatModel();
  const structuredModel = model.withStructuredOutput(routingSchema);

  const systemPrompt = `You are the Event Lead Supervisor managing an event team: ${members.join(', ')}.
Analyze the conversation and choose the best specialized agent:
- Query about sponsorship, tiers, pricing, perks, or corporate packages -> route to "SponsorAgent".
- Query about social media, tweets, promo posts, marketing -> route to "MarketingAgent".
- Query about venue layout, room capacity, stage, Wi-Fi, equipment, logistics -> route to "VenueAgent".
- Query answered satisfactorily or general greeting -> route to "FINISH".`;

  const result = await structuredModel.invoke([
    new SystemMessage(systemPrompt),
    ...state.messages,
  ]);

  return {
    next: result.next,
    traces: [
      `👑 Supervisor [LangGraph]: Routing decision -> ${result.next} (${result.reasoning})`,
    ],
  };
}
