import React, { useState } from "react";
import "./Chatbot.css";
import axios from "axios";

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { text: "Hi! How can I help you?", isBot: true },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, isBot: false }];
    setMessages(newMessages);
    setInput("");

    try {
      const response = await axios.post("http://127.0.0.1:5000/prompt", {
        prompt: input,
      });

      const items =
        response.data.match(/\d+\.\s\*\*.*?\*\*:.*?(?=\d+\.|$)/gs) || [];

      const defaultMessage = { text: response.data.reply, isBot: true };

      const responseMessage = {
        text: (
          <ol>
            {items.map((item, index) => {
              const [name, description] = item
                .split(": ")
                .map((part) => part.replace(/^\d+\.\s\*\*|\*\*/g, "").trim());
              return (
                <li key={index}>
                  <strong>{name}</strong>: {description}
                </li>
              );
            })}
          </ol>
        ),
        isBot: true,
      };

      if (responseMessage.text) {
        setMessages((prevMessages) => [...prevMessages, responseMessage]);
      } else {
        setMessages((prevMessages) => [...prevMessages, defaultMessage]);
      }

      console.log("JSON Reply:", response.data);
      return response.data;
    } catch (error) {
      console.error("Cannot fetch the default response: ", error);
      const errorMessage = {
        text: "Sorry, something went wrong.",
        isBot: true,
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    }
  };

  return (
    <div className="chatbot">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isBot ? "bot" : "user"}`}>
            <span className="message-text">{msg.text}</span>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button className='button' onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
