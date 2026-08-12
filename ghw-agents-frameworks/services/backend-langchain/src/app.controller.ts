import { Controller, Post, Body, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('api')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('health')
  getHealth() {
    return { status: 'ok', framework: 'LangChain', port: 4000 };
  }

  @Post('chat')
  async chat(@Body() body: { message: string; sessionId: string }) {
    const { reply, traces, activeAgents } = await this.appService.runAgent(
      body.message,
    );
    return { reply, traces, activeAgents, framework: 'LangChain' };
  }
}
