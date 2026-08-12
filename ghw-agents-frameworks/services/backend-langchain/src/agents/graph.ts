import { StateGraph, START, END } from '@langchain/langgraph';
import { EventState } from './state';
import { supervisorNode } from './definitions/supervisor.agent';
import { sponsorAgentNode } from './definitions/sponsor.agent';
import { marketingAgentNode } from './definitions/marketing.agent';
import { venueAgentNode } from './definitions/venue.agent';
import { cateringAgentNode } from './definitions/catering.agent';

// Assemble the LangGraph StateGraph
const workflow = new StateGraph(EventState)
  .addNode('supervisor', supervisorNode)
  .addNode('SponsorAgent', sponsorAgentNode)
  .addNode('MarketingAgent', marketingAgentNode)
  .addNode('VenueAgent', venueAgentNode)
  .addNode('CateringAgent', cateringAgentNode)
  .addEdge(START, 'supervisor')
  .addConditionalEdges('supervisor', (x) => x.next, {
    SponsorAgent: 'SponsorAgent',
    MarketingAgent: 'MarketingAgent',
    CateringAgent: 'CateringAgent',
    VenueAgent: 'VenueAgent',
    FINISH: END,
  })
  .addEdge('SponsorAgent', 'supervisor')
  .addEdge('MarketingAgent', 'supervisor')
  .addEdge('VenueAgent', 'supervisor')
  .addEdge('CateringAgent', 'supervisor');

export const eventGraphApp = workflow.compile();
