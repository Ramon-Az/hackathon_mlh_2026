import { tool } from '@langchain/core/tools';
import { z } from 'zod';

export const getSponsorshipPackagesTool = tool(
  ({ tier }) => {
    const t = tier.toLowerCase();
    if (t.includes('gold')) {
      return Promise.resolve(
        'Gold Tier ($5,000): Main Stage branding, 5 free VIP tickets, Keynote speaking slot, Premier booth placement.',
      );
    } else if (t.includes('silver')) {
      return Promise.resolve(
        'Silver Tier ($2,500): Logo on website & swag bags, 2 VIP tickets, Standard booth placement.',
      );
    } else if (t.includes('bronze')) {
      return Promise.resolve(
        'Bronze Tier ($1,000): Logo on website, 1 ticket.',
      );
    }
    return Promise.resolve(
      'Available tiers: Gold ($5000), Silver ($2500), Bronze ($1000). Ask for specifics on any tier!',
    );
  },
  {
    name: 'get_sponsorship_packages',
    description:
      'Calculates price, benefits, and perk details for sponsorship tiers (gold, silver, bronze).',
    schema: z.object({
      tier: z
        .string()
        .describe('The sponsorship tier requested (gold, silver, or bronze)'),
    }),
  },
);
