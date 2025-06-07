import type { ChatInputProps } from "@types";
import React, { useState, type KeyboardEvent } from "react";
import { IoSend } from "react-icons/io5";

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  className = "",
}) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`chat-input ${className}`}>
      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder=""
            disabled={disabled}
            rows={1}
            className="message-input"
          />
          <button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            className="send-button"
            aria-label="Enviar mensaje"
          >
            <IoSend size={36} />
          </button>
        </div>
      </div>
      <div className="input-footer">
        <p className="disclaimer">
          BASF Assistant puede cometer errores. Verifica información importante
          sobre productos químicos y soluciones.
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
