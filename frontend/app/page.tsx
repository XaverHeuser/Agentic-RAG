"use client";

import { useState } from "react";
// 1. IMPORT THE LIBRARY
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Corrected FastAPI endpoint
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) throw new Error("API call failed");

      const data = await response.json();
      
      const assistantMessage: Message = { 
        role: "assistant", 
        content: data.answer // The agent's full Markdown response
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error calling API:", error);
      setMessages((prev) => [...prev, {role: "assistant", content: "⚠️ Fehler bei der Verbindung zum Agenten."}]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex flex-col h-screen max-w-3xl mx-auto p-4 antialiased">
      <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">🎓 ScholarAgent</h1>
      
      {/* Message Area */}
      <div className="flex-1 overflow-y-auto border rounded-lg p-6 space-y-5 bg-white shadow-inner">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] p-4 rounded-xl ${
              msg.role === "user" ? "bg-blue-600 text-white shadow-md" : "bg-gray-100 border text-black"
            }`}>
              
              {/* 2. THE FIX: WRAP REACT-MARKDOWN IN A DIV INSTEAD */}
            <div className={`prose ${msg.role === "user" ? "prose-invert" : ""} max-w-none text-sm md:text-base leading-relaxed`}>
              <ReactMarkdown>
                {msg.content}
              </ReactMarkdown>
            </div>

            </div>
          </div>
        ))}
        {isLoading && <div className="text-gray-400 animate-pulse pl-4 text-sm">Agent analysiert Dokumente...</div>}
      </div>

      {/* Input Area */}
      <div className="mt-5 flex gap-3 pb-2">
        <input
          className="flex-1 border rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Frag etwas über deine Dokumente..."
        />
        <button 
          onClick={sendMessage}
          disabled={isLoading}
          className="bg-blue-600 text-white px-7 py-3 rounded-xl font-medium hover:bg-blue-700 disabled:bg-gray-300 transition shadow-md"
        >
          Senden
        </button>
      </div>
    </main>
  );
}
