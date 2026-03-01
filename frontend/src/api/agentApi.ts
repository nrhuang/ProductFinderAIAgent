import type { ChatRequest, ChatResponse } from "../types";

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}
