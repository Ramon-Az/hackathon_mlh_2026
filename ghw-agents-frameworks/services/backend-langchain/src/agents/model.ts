import { ChatGoogleGenerativeAI } from '@langchain/google-genai';

export function getChatModel(): ChatGoogleGenerativeAI {
  const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  const model =
    process.env.GEMINI_MODEL || process.env.MODEL_NAME || 'gemini-3.5-flash';

  return new ChatGoogleGenerativeAI({
    model,
    temperature: 0,
    apiKey,
  });
}
