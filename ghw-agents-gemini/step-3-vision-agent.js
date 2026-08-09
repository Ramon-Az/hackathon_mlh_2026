import { GoogleGenAI } from "@google/genai";
import "dotenv/config";
import * as fs from "node:fs";

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

// Read the image from your computer
// and convert it to base64 so we can send it to Gemini.
const imageData = fs.readFileSync("demo2-image.jpg", {
  encoding: "base64",
});

const response = await ai.models.generateContent({
  model: "gemini-3.6-flash",

  contents: [
    {
      inlineData: {
        mimeType: "image/jpeg",
        data: imageData,
      },
    },
    {
      text: `
        You are a smart visual assistant.

        Analyze this image and tell me:

        1. What you can see
        2. What you think is happening
        3. Three useful observations or recommendations

        Keep your answer beginner-friendly and concise.
      `,
    },
  ],
});

console.log("\n👀 Gemini Vision Agent\n");
console.log(response.text);