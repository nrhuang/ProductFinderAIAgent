import type { Message } from "../types";
import ProductGrid from "./ProductGrid";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "message-row--user" : "message-row--agent"}`}>
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
      {!isUser && message.products.length > 0 && (
        <ProductGrid products={message.products} />
      )}
    </div>
  );
}
