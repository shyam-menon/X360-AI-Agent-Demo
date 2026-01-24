import { GoogleGenAI, Schema, Type } from "@google/genai";
import { RAW_CHAOTIC_DATA, SYSTEM_INSTRUCTION_NIGHT_WATCHMAN, SYSTEM_INSTRUCTION_CHAT } from "../constants";
import { BriefingResponse, ChatMessage } from "../types";

// Initialize Gemini
// NOTE: We use process.env.API_KEY as per instructions.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

// Schema for the Morning Briefing to ensure strictly typed JSON
const BRIEFING_SCHEMA: Schema = {
  type: Type.OBJECT,
  properties: {
    summary: { type: Type.STRING },
    items: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          id: { type: Type.STRING },
          type: { type: Type.STRING, enum: ["SLA_BREACH", "DATA_CONFLICT", "INSIGHT"] },
          title: { type: Type.STRING },
          description: { type: Type.STRING },
          severity: { type: Type.STRING, enum: ["CRITICAL", "HIGH", "MEDIUM", "LOW"] },
          relatedTicketIds: { 
            type: Type.ARRAY, 
            items: { type: Type.STRING } 
          },
          suggestedAction: { type: Type.STRING }
        },
        required: ["id", "type", "title", "description", "severity", "relatedTicketIds"]
      }
    }
  },
  required: ["summary", "items"]
};

export const runMorningBriefing = async (): Promise<BriefingResponse> => {
  try {
    const dataContext = JSON.stringify(RAW_CHAOTIC_DATA, null, 2);
    
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview", // Efficient for analysis
      contents: `Here is the raw data from the virtualization layer: \n${dataContext}`,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION_NIGHT_WATCHMAN,
        responseMimeType: "application/json",
        responseSchema: BRIEFING_SCHEMA,
        temperature: 0.2, // Low temperature for factual analysis
      }
    });

    if (response.text) {
      return JSON.parse(response.text) as BriefingResponse;
    }
    throw new Error("No response from Gemini");
  } catch (error) {
    console.error("Gemini Briefing Error:", error);
    // Fallback if API fails or key is missing, so demo doesn't crash entirely
    return {
      summary: "System is offline. Displaying cached operational data.",
      items: []
    };
  }
};

export const sendChatMessage = async (history: ChatMessage[], newMessage: string): Promise<string> => {
  try {
    const dataContext = JSON.stringify(RAW_CHAOTIC_DATA, null, 2);
    
    // Construct chat history for the model
    // We inject the data context into the system instruction or the first turn
    const chat = ai.chats.create({
      model: "gemini-3-flash-preview",
      config: {
        systemInstruction: `${SYSTEM_INSTRUCTION_CHAT}\n\nCURRENT DATASET:\n${dataContext}`,
      }
    });

    // Replay history (filtering out our internal 'isAction' flag if we had one)
    // Note: In a real app we'd map this properly to Content objects, but for this demo simple strings work well with the helper
    // However, the helper keeps state, so we just send the new message with context if needed.
    // For simplicity in this demo, we'll just do a single turn generation with history context appended, 
    // or use the chat object if we wanted a true session. 
    // Let's use the chat object properly but we need to feed it previous messages manually if we recreate it.
    // To keep it simple and stateless for the demo service:
    
    const conversation = history.map(h => `${h.role === 'user' ? 'User' : 'Agent'}: ${h.content}`).join('\n');
    const prompt = `${conversation}\nUser: ${newMessage}\nAgent:`;

    const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: prompt,
        config: {
            systemInstruction: `${SYSTEM_INSTRUCTION_CHAT}\n\nCURRENT DATASET:\n${dataContext}`,
        }
    });

    return response.text || "I apologize, I couldn't process that.";

  } catch (error) {
    console.error("Gemini Chat Error:", error);
    return "I am having trouble connecting to the X360 core. Please check your connection.";
  }
};
