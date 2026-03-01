import { useState, useRef, type FormEvent } from "react";
import type { Message } from "./types";
import { sendMessage } from "./api/agentApi";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const query = input.trim();
    if (!query || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: query,
      products: [],
    };

    const pendingId = crypto.randomUUID();
    const pendingMsg: Message = {
      id: pendingId,
      role: "agent",
      text: "__loading__",
      products: [],
    };

    setMessages((prev) => [...prev, userMsg, pendingMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendMessage({ query, session_id: sessionId });

      const agentMsg: Message = {
        id: pendingId,
        role: "agent",
        text: response.text,
        products: response.products ?? [],
      };

      setMessages((prev) =>
        prev.map((m) => (m.id === pendingId ? agentMsg : m))
      );
    } catch {
      const errorMsg: Message = {
        id: pendingId,
        role: "agent",
        text: "Sorry, I couldn't connect. Please try again.",
        products: [],
      };
      setMessages((prev) =>
        prev.map((m) => (m.id === pendingId ? errorMsg : m))
      );
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Product Finder</h1>
        <p>Ask me anything about our products</p>
      </header>

      <main className="app-main">
        <ChatWindow messages={messages} />
      </main>

      <footer className="app-footer">
        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            className="chat-input"
            type="text"
            placeholder="e.g. Show me electronics under $200"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            className="chat-submit"
            type="submit"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}
