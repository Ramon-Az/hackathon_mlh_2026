import { tool } from '@langchain/core/tools';
import { z } from 'zod';

export const getVenueDetailsTool = tool(
  ({ area }) => {
    const a = area.toLowerCase();
    if (a.includes('main') || a.includes('hall')) {
      return Promise.resolve(
        'Main Stage Hall: Capacity 500 people, Dual 4K Projectors, Surround Sound, Keynote Stage.',
      );
    } else if (a.includes('workshop') || a.includes('room')) {
      return Promise.resolve(
        'Workshop Rooms A & B: Capacity 60 people each, Whiteboards, High-density Wi-Fi, Dedicated power outlets.',
      );
    } else if (a.includes('lounge') || a.includes('networking')) {
      return Promise.resolve(
        'Networking Lounge: Capacity 150 people, Standing tables, Soft seating, Refreshment counter.',
      );
    }
    return Promise.resolve(
      'Venue Info: Tech Convention Center (Total Capacity: 800). Facilities: Main Stage, Workshop Rooms A/B, Networking Lounge. High-speed Wi-Fi across all areas.',
    );
  },
  {
    name: 'get_venue_details',
    description:
      'Gets information about venue rooms, capacity, Wi-Fi, and equipment.',
    schema: z.object({
      area: z
        .string()
        .describe('Room or area name e.g. Main Hall, Workshop, Lounge'),
    }),
  },
);
