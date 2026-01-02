import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <form onSubmit={submit} className="flex gap-2 mt-2">
      <input
        className="flex-1 border rounded px-3 py-2"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about dengue..."
      />
      <button className="bg-indigo-600 text-white px-4 py-2 rounded">
        Send
      </button>
    </form>
  );
}
