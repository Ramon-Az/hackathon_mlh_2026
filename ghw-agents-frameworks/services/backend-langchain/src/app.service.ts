import { Injectable } from '@nestjs/common';
import { runLeadAgent } from './agents/lead';

@Injectable()
export class AppService {
  async runAgent(
    message: string,
  ): Promise<{ reply: string; traces: string[]; activeAgents: string[] }> {
    return await runLeadAgent(message);
  }
}
