import { useEffect, useRef } from "react";
import type { Message } from "../types";
import MessageBubble from "./MessageBubble";

const SUGGESTIONS = [
  "Show me all electronics",
  "What do you have under $10?",
  "Clothing or accessories under $50",
  "Anything but groceries",
];

interface ChatWindowProps {
  messages: Message[];
  onSuggestionClick: (query: string) => void;
  showSuggestions: boolean;
}

export default function ChatWindow({ messages, onSuggestionClick, showSuggestions }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {showSuggestions && (
        <div className="suggestions">
          {SUGGESTIONS.map((text) => (
            <button
              key={text}
              className="suggestions__pill"
              onClick={() => onSuggestionClick(text)}
            >
              {text}
            </button>
          ))}
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
