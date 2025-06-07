import type {
  BaseComponent,
  ChatMessage as ChatMessageType,
  ChatState,
} from "@types";
import React, { useEffect, useRef, useState } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

interface ChatProps extends BaseComponent {}

const Chat: React.FC<ChatProps> = ({ className = "" }) => {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [
      {
        id: "1",
        content:
          "¡Hola! Soy el asistente de BASF. Estoy aquí para ayudarte con información sobre química, sostenibilidad, productos e innovaciones de BASF. ¿En qué puedo ayudarte hoy?",
        role: "assistant",
        timestamp: new Date(),
      },
    ],
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

  const generateResponse = (userMessage: string): string => {
    const responses = {
      // Saludos
      greetings: [
        "¡Hola! Me alegra poder ayudarte. Soy tu asistente especializado en BASF.",
        "¡Bienvenido! Estoy aquí para responder tus preguntas sobre BASF y química.",
        "¡Hola! ¿En qué aspecto de BASF te gustaría que te ayude hoy?",
      ],

      // BASF información general
      basf: [
        'BASF es la empresa química líder en el mundo. Nuestro propósito corporativo es "We create chemistry for a sustainable future" (Creamos química para un futuro sostenible). Combinamos el éxito económico con la protección del medio ambiente y la responsabilidad social.',
        "BASF fue fundada en 1865 y tiene su sede en Ludwigshafen, Alemania. Operamos en más de 80 países y tenemos aproximadamente 111,000 empleados en todo el mundo.",
        "En BASF, nos enfocamos en la química inteligente que permite un futuro más sostenible. Nuestro concepto Verbund conecta plantas de producción, cadenas de valor y tecnologías.",
      ],

      // Sostenibilidad
      sustainability: [
        "La sostenibilidad está en el corazón de nuestra estrategia. Trabajamos en soluciones que contribuyen a un futuro más sostenible, desde materiales para vehículos eléctricos hasta productos para agricultura sostenible.",
        "Nuestro objetivo es lograr emisiones netas cero para 2050. Estamos invirtiendo en tecnologías innovadoras como la producción de hidrógeno verde y procesos de fabricación con bajas emisiones de CO2.",
        "BASF desarrolla productos que ayudan a nuestros clientes a ser más sostenibles. Por ejemplo, nuestros catalizadores para automóviles reducen las emisiones y nuestros materiales de construcción mejoran la eficiencia energética.",
      ],

      // Productos
      products: [
        "BASF produce una amplia gama de productos: químicos, materiales de rendimiento, soluciones industriales, tecnologías de superficie, nutrición y cuidado, y soluciones agrícolas.",
        "Nuestros productos van desde químicos básicos hasta soluciones especializadas para industrias como automotriz, construcción, agricultura, cuidado personal y farmacéutica.",
        "Algunos de nuestros productos más conocidos incluyen catalizadores, espumas, recubrimientos, productos para cuidado del hogar y soluciones para protección de cultivos.",
      ],

      // Innovación
      innovation: [
        "La innovación es clave para BASF. Invertimos aproximadamente €2 mil millones anuales en investigación y desarrollo, trabajando en más de 3,000 proyectos de I+D.",
        "Nuestros centros de innovación están distribuidos globalmente, colaborando con universidades, startups y otros socios para desarrollar soluciones del futuro.",
        "Estamos trabajando en tecnologías revolucionarias como baterías para vehículos eléctricos, procesos de producción digitalizados y nuevos materiales sostenibles.",
      ],

      // Default
      default: [
        "Esa es una excelente pregunta sobre BASF. Te recomiendo visitar nuestro sitio web oficial para obtener información más detallada y actualizada.",
        "Como empresa química líder, BASF tiene muchos aspectos fascinantes. ¿Te gustaría saber más sobre algún área específica como sostenibilidad, productos o innovación?",
        "BASF es una empresa muy diversa. ¿Hay algún sector o producto específico de BASF sobre el que te gustaría aprender más?",
      ],
    };

    const message = userMessage.toLowerCase();

    if (
      message.includes("hola") ||
      message.includes("hi") ||
      message.includes("hello")
    ) {
      return responses.greetings[
        Math.floor(Math.random() * responses.greetings.length)
      ];
    }

    if (
      message.includes("basf") ||
      message.includes("empresa") ||
      message.includes("compañía")
    ) {
      return responses.basf[Math.floor(Math.random() * responses.basf.length)];
    }

    if (
      message.includes("sostenib") ||
      message.includes("medio ambiente") ||
      message.includes("verde") ||
      message.includes("co2")
    ) {
      return responses.sustainability[
        Math.floor(Math.random() * responses.sustainability.length)
      ];
    }

    if (
      message.includes("producto") ||
      message.includes("químico") ||
      message.includes("material")
    ) {
      return responses.products[
        Math.floor(Math.random() * responses.products.length)
      ];
    }

    if (
      message.includes("innovac") ||
      message.includes("investigac") ||
      message.includes("tecnolog") ||
      message.includes("futuro")
    ) {
      return responses.innovation[
        Math.floor(Math.random() * responses.innovation.length)
      ];
    }

    return responses.default[
      Math.floor(Math.random() * responses.default.length)
    ];
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

    // Simulate API delay
    setTimeout(() => {
      const response = generateResponse(content);
      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        content: response,
        role: "assistant",
        timestamp: new Date(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: prev.messages
          .filter((m) => m.id !== "typing")
          .concat(assistantMessage),
        isLoading: false,
      }));
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  return (
    <div className={`chat-container ${className}`}>
      <div className="chat-header">
        <div className="header-content">
          <div className="basf-brand">
            <div className="basf-logo-header">
              <span className="basf-text">BASF</span>
              <div className="logo-squares-header">
                <div className="square-header square-1"></div>
                <div className="square-header square-2"></div>
              </div>
            </div>
            <div className="brand-claim">We create chemistry</div>
          </div>
          <div className="microsoft-brand">
            <div className="microsoft-logo">
              <div className="microsoft-squares">
                <div className="ms-square ms-red"></div>
                <div className="ms-square ms-green"></div>
                <div className="ms-square ms-blue"></div>
                <div className="ms-square ms-yellow"></div>
              </div>
              <span className="microsoft-text">Microsoft</span>
            </div>
            <div className="hackathon-label">Hackathon Partner</div>
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
    </div>
  );
};

export default Chat;
