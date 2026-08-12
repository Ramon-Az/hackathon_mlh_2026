import { tool } from '@langchain/core/tools';
import { z } from 'zod';

export const generateMarketingPostTool = tool(
  ({ platform, topic }) => {
    return Promise.resolve(
      `📢 [Draft for ${platform}]: "🚀 Big news regarding ${topic}! Join us at EventCraft AI Hackathon! Register today: eventcraft.ai #Hackathon #AI"`,
    );
  },
  {
    name: 'generate_marketing_post',
    description:
      'Generates tailored social media posts and promo text for specific platforms.',
    schema: z.object({
      platform: z
        .string()
        .describe('Target platform (e.g., Twitter/X, LinkedIn, Instagram)'),
      topic: z.string().describe('The topic or announcement to promote'),
    }),
  },
);
