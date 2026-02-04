import { BriefingResponse, ChatMessage, Ticket, Citation } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Run morning briefing analysis on virtualization layer data.
 * Replaces the Gemini-based runMorningBriefing.
 */
export const runMorningBriefing = async (data: Ticket[]): Promise<BriefingResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/briefing`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ data })
    });

    if (!response.ok) {
      throw new Error(`Briefing request failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Backend Briefing Error:', error);
    // Fallback if API fails
    return {
      summary: "System is offline. Displaying cached operational data.",
      items: []
    };
  }
};

/**
 * Send a chat message to the AI agent (ASK or DO mode).
 * Replaces the Gemini-based sendChatMessage.
 */
export const sendChatMessage = async (
  history: ChatMessage[],
  newMessage: string,
  mode: 'ASK' | 'DO',
  context?: {
    data?: Ticket[];
    briefing?: BriefingResponse;
  }
): Promise<{ response: string; citations?: Citation[] }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: newMessage,
        history,
        mode,
        context
      })
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('[CITATIONS DEBUG] Backend response:', {
      hasResponse: !!result.response,
      hasCitations: !!result.citations,
      citationsCount: result.citations?.length || 0,
      citations: result.citations
    });
    return {
      response: result.response,
      citations: result.citations
    };
  } catch (error) {
    console.error('Backend Chat Error:', error);
    return {
      response: "I am having trouble connecting to the X360 core. Please check your connection.",
      citations: undefined
    };
  }
};

/**
 * Check if the backend API is healthy.
 */
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    return response.ok;
  } catch {
    return false;
  }
};
