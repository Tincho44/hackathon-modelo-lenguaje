import type { MessageProps } from "@types";
import React from "react";

const ChatMessage: React.FC<MessageProps> = ({ message, className = "" }) => {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  // Function to format message content
  const formatMessageContent = (content: string) => {
    // First, handle the main structure
    const sections = content.split(/(?=\*\*(Alerta|Recomendación))/i);

    return sections
      .map((section, sectionIndex) => {
        if (section.trim() === "") return null;

        const elements: React.ReactElement[] = [];

        // Check if it's an alert or recommendation header
        if (section.match(/^\*\*(Alerta|Recomendación)/i)) {
          const headerMatch = section.match(/^(\*\*[^*]+\*\*[^:]*:?\s*)(.*)/s);
          if (headerMatch) {
            const [, header, rest] = headerMatch;
            elements.push(
              <div key={`header-${sectionIndex}`} className="alert-header">
                {formatInlineText(header)}
              </div>
            );

            if (rest.trim()) {
              const listItems = rest.split(/(?=\d+\.\s*\*\*)/);
              listItems.forEach((item, itemIndex) => {
                if (item.trim()) {
                  const numberedMatch = item.match(
                    /^(\d+\.\s*)(\*\*[^*]+\*\*:?\s*)(.*)/s
                  );
                  if (numberedMatch) {
                    const [, number, boldTitle, description] = numberedMatch;
                    elements.push(
                      <div
                        key={`item-${sectionIndex}-${itemIndex}`}
                        className="numbered-item"
                      >
                        <span className="number">{number}</span>
                        <div className="content">
                          <div className="item-title">
                            {formatInlineText(boldTitle)}
                          </div>
                          {description.trim() && (
                            <div className="item-description">
                              {formatInlineText(description)}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  } else {
                    elements.push(
                      <div
                        key={`text-${sectionIndex}-${itemIndex}`}
                        className="message-line"
                      >
                        {formatInlineText(item.trim())}
                      </div>
                    );
                  }
                }
              });
            }
          }
        } else {
          // Handle regular content
          const lines = section.split("\n").filter((line) => line.trim());
          lines.forEach((line, lineIndex) => {
            elements.push(
              <div
                key={`line-${sectionIndex}-${lineIndex}`}
                className="message-line"
              >
                {formatInlineText(line)}
              </div>
            );
          });
        }

        return (
          <div key={sectionIndex} className="content-section">
            {elements}
          </div>
        );
      })
      .filter(Boolean);
  };

  // Function to format inline text (bold, etc.)
  const formatInlineText = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/);

    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        const boldText = part.slice(2, -2);
        return (
          <strong key={index} className="bold-text">
            {boldText}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div
      className={`chat-message ${isUser ? "user" : "assistant"} ${className}`}
    >
      <div className="message-container">
        {isAssistant && (
          <div className="assistant-avatar">
            <div className="company_name-logo">
            </div>
          </div>
        )}

        <div className="message-content">
          {isAssistant && (
            <div className="message-header">
              <span className="sender-name">COMPANY_NAME Assistant</span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          )}

          <div className="message-bubble">
            {message.isTyping ? (
              <div className="typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            ) : (
              <div className="formatted-content">
                {formatMessageContent(message.content)}
              </div>
            )}
          </div>

          {isUser && (
            <div className="message-time user-time">
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          )}
        </div>

        {isUser && (
          <div className="user-avatar">
            <div className="user-icon">👤</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
