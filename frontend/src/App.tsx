import { useState, useRef, type FormEvent } from "react";
import type { Message } from "./types";
import { sendMessage } from "./api/agentApi";
import ChatWindow from "./components/ChatWindow";

const greetingMessage: Message = {
  id: "greeting",
  role: "agent",
  text: "Hey! I'm your Product Finder assistant. Ask me about any product — I can search and recommend items for you.",
  products: [],
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([greetingMessage]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const inputRef = useRef<HTMLInputElement>(null);

  async function sendQuery(query: string) {
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

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendQuery(input.trim());
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__icon">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L13.09 8.26L18 6L14.74 10.91L21 12L14.74 13.09L18 18L13.09 15.74L12 22L10.91 15.74L6 18L9.26 13.09L3 12L9.26 10.91L6 6L10.91 8.26L12 2Z" />
          </svg>
        </div>
        <div>
          <h1>Product Finder</h1>
          <p>Ask me anything about our products</p>
        </div>
      </header>

      <main className="app-main">
        <ChatWindow
          messages={messages}
          onSuggestionClick={sendQuery}
          showSuggestions={messages.length === 1}
        />
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
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </form>
      </footer>
    </div>
  );
}
