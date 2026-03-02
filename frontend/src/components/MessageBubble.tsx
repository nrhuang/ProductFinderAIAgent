import type { Message } from "../types";
import ProductGrid from "./ProductGrid";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "message-row--user" : "message-row--agent"}`}>
      <div className="message-content">
        {!isUser && (
          <div className="agent-avatar">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1.07A7 7 0 0 1 14 23h-4a7 7 0 0 1-6.93-4H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 12 2zm-2 9a5 5 0 0 0-5 5v1a5 5 0 0 0 5 5h4a5 5 0 0 0 5-5v-1a5 5 0 0 0-5-5h-4zm-1 5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zm6 0a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z" />
            </svg>
          </div>
        )}
        <div className={`message-bubble ${isUser ? "message-bubble--user" : "message-bubble--agent"}`}>
          {message.text === "__loading__" ? (
            <span className="typing-dots">
              <span />
              <span />
              <span />
            </span>
          ) : (
            message.text
          )}
        </div>
      </div>
      {!isUser && message.products.length > 0 && (
        <ProductGrid products={message.products} />
      )}
    </div>
  );
}
