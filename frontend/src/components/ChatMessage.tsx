import type { MessageProps } from "@types";
import React from "react";

const ChatMessage: React.FC<MessageProps> = ({ message, className = "" }) => {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={`chat-message ${isUser ? "user" : "assistant"} ${className}`}
    >
      <div className="message-container">
        {isAssistant && (
          <div className="assistant-avatar">
            <div className="basf-logo">
              <span>BASF</span>
              <div className="logo-squares">
                <div className="square square-1"></div>
                <div className="square square-2"></div>
              </div>
            </div>
          </div>
        )}

        <div className="message-content">
          {isAssistant && (
            <div className="message-header">
              <span className="sender-name">BASF Assistant</span>
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
              <p>{message.content}</p>
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
