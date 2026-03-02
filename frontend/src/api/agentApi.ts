import type { ChatRequest, ChatResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}
