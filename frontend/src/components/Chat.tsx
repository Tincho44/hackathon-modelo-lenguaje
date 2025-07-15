import type {
  BaseComponent,
  ChatMessage as ChatMessageType,
  ChatState,
} from "@types";
import React, { useEffect, useRef, useState } from "react";
import { apiService } from "../services/api";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

const Chat: React.FC<BaseComponent> = ({ className = "" }) => {
  const getUrlParameter = (name: string): string | null => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  };

  const getInitialMessages = (): ChatMessageType[] => {
    const contextData = getUrlParameter("data");

    if (contextData) {
      const decodedMessage = decodeURIComponent(contextData);
      console.log("🔗 CONTEXTO DETECTADO EN URL:");
      console.log("   Mensaje decodificado:", decodedMessage);

      return [
        {
          id: "context-message",
          content: decodedMessage,
          role: "assistant",
          timestamp: new Date(),
        },
      ];
    }

    return [
      {
        id: "1",
        content:
          "¡Hola! Soy el asistente de COMPANY_NAME. Estoy aquí para ayudarte con información sobre química, sostenibilidad, productos e innovaciones de COMPANY_NAME. ¿En qué puedo ayudarte hoy?",
        role: "assistant",
        timestamp: new Date(),
      },
    ];
  };

  const [chatState, setChatState] = useState<ChatState>({
    messages: getInitialMessages(),
    isLoading: false,
    error: null,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatState.messages]);

  // Effect to clean URL after loading context
  useEffect(() => {
    const contextData = getUrlParameter("data");
    if (contextData) {
      // Clean the URL by removing the data parameter
      const url = new URL(window.location.href);
      url.searchParams.delete("data");
      window.history.replaceState(
        {},
        document.title,
        url.pathname + url.search
      );
      console.log("🔗 URL limpiada después de cargar contexto");
    }
  }, []);

  const handleDownloadReport = async () => {
    try {
      console.log("📄 Generating report for conversation...");

      // Prepare conversation data
      const conversationData = {
        messages: chatState.messages.filter((msg) => !msg.isTyping), // Exclude typing indicators
        timestamp: new Date().toISOString(),
      };

      // Generate and download PDF
      const pdfBlob = await apiService.generateReport(conversationData);

      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      link.href = url;

      // Generate filename with timestamp
      const timestamp = new Date()
        .toLocaleString("es-ES")
        .replace(/[/,:]/g, "-")
        .replace(/\s/g, "_");
      link.download = `COMPANY_NAME_Reporte_Incidente_${timestamp}.pdf`;

      // Trigger download
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log("✅ Report downloaded successfully");
    } catch (error) {
      console.error("❌ Error downloading report:", error);
      // You could add a toast notification here
    }
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setChatState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    // Add typing indicator
    const typingMessage: ChatMessageType = {
      id: "typing",
      content: "",
      role: "assistant",
      timestamp: new Date(),
      isTyping: true,
    };

    setChatState((prev) => ({
      ...prev,
      messages: [...prev.messages, typingMessage],
    }));

    try {
      console.log("🤖 Enviando consulta al LLM:", content);
      console.log("⏰ Timestamp:", new Date().toISOString());

      // Call real LLM API with very cold/concise parameters with timeout
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(
          () => reject(new Error("Request timeout after 30 seconds")),
          30000
        )
      );

      const apiPromise = apiService.queryLLM(
        content,
        undefined, // document_name
        0.1 // temperature: very cold (0.0-1.0, lower = more deterministic)
      );

      console.log("🔄 Waiting for LLM response...");
      const response = (await Promise.race([apiPromise, timeoutPromise])) as {
        answer: string;
        sources: any[];
        context_url: string;
      };

      console.log("✅ Respuesta del LLM recibida:", response);
      console.log("🔗 URL de contexto generada:", response.context_url);
      console.log("⏰ Response timestamp:", new Date().toISOString());

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        role: "assistant",
        timestamp: new Date(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: prev.messages
          .filter((m) => m.id !== "typing")
          .concat(assistantMessage),
        isLoading: false,
        error: null,
      }));
    } catch (error) {
      console.error("❌ Error al consultar el LLM:", error);

      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        content:
          "Lo siento, ha ocurrido un error al procesar tu consulta. Por favor, inténtalo de nuevo.",
        role: "assistant",
        timestamp: new Date(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: prev.messages
          .filter((m) => m.id !== "typing")
          .concat(errorMessage),
        isLoading: false,
        error: "Error al conectar con el LLM",
      }));
    }
  };

  return (
    <div className={`chat-container ${className}`}>
      <div className="chat-header">
        <div className="header-content">
          <div className="company_name-brand">
            <div className="company_name-logo-header">
              <span className="company_name-text">COMPANY_NAME</span>
            </div>
            <div className="brand-claim">company slogan</div>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {chatState.messages.map((message, index) => (
          <ChatMessage
            key={message.id}
            message={message}
            isLatest={index === chatState.messages.length - 1}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={chatState.isLoading}
        placeholder=""
      />

      {/* Floating Download Report Button */}
      <button
        onClick={handleDownloadReport}
        className="floating-download-btn"
        title="Descargar reporte PDF"
        disabled={chatState.messages.length <= 1}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M12 15L7 10H11V3H13V10H17L12 15Z" fill="currentColor" />
          <path d="M20 18H4V20H20V18Z" fill="currentColor" />
        </svg>
      </button>
    </div>
  );
};

export default Chat;
