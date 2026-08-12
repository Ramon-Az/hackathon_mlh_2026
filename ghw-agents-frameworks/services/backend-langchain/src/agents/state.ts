import { Annotation } from '@langchain/langgraph';
import { BaseMessage } from '@langchain/core/messages';

export const EventState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
  next: Annotation<string>({
    reducer: (x, y) => y ?? x,
    default: () => 'supervisor',
  }),
  traces: Annotation<string[]>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
});
