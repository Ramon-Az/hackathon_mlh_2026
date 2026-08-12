import { tool } from '@langchain/core/tools';
import { z } from 'zod';

export const getCateringPackagesTool = tool(
  ({ packageType }) => {
    const p = packageType.toLowerCase();
    if (p.includes('standard')) {
      return Promise.resolve(
        'Standard Catering Package ($20/person): Includes 2 appetizers, 2 main courses, 1 dessert, and non-alcoholic beverages.',
      );
    } else if (p.includes('premium')) {
      return Promise.resolve(
        'Premium Catering Package ($35/person): Includes 3 appetizers, 3 main courses, 2 desserts, and a selection of alcoholic and non-alcoholic beverages.',
      );
    } else if (p.includes('deluxe')) {
      return Promise.resolve(
        'Deluxe Catering Package ($50/person): Includes 4 appetizers, 4 main courses, 3 desserts, premium beverage options, and a dedicated catering staff.',
      );
    }
    return Promise.resolve(
      'Available packages: Standard ($20/person), Premium ($35/person), Deluxe ($50/person). Ask for specifics on any package!',
    );
  },
  {
    name: 'get_catering_packages',
    description:
      'Calculates price, menu options, and details for catering packages (standard, premium, deluxe).',
    schema: z.object({
      packageType: z
        .string()
        .describe(
          'The catering package requested (standard, premium, or deluxe)',
        ),
    }),
  },
);

export const getCateringEstimateTool = tool(
  ({ numGuests }) => {
    const guests = Number(numGuests);
    if (isNaN(guests) || guests <= 0) {
      return Promise.resolve(
        'Please provide a valid number of guests greater than 0.',
      );
    }
    const standardCost = guests * 20;
    const premiumCost = guests * 35;
    const deluxeCost = guests * 50;

    return Promise.resolve(
      `Estimated Catering Costs for ${guests} guests:\n- Standard Package: $${standardCost}\n- Premium Package: $${premiumCost}\n- Deluxe Package: $${deluxeCost}`,
    );
  },
  {
    name: 'get_catering_estimate',
    description:
      'Calculates estimated catering costs based on the number of guests.',
    schema: z.object({
      numGuests: z
        .number()
        .int()
        .min(1)
        .describe('The number of guests for the catering estimate'),
    }),
  },
);
