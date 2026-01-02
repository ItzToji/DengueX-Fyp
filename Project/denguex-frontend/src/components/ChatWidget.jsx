import { useState } from "react";
import Chatbot from "./Chatbot";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 bg-indigo-600 text-white p-4 rounded-full shadow-lg"
      >
        💬
      </button>

      {open && (
        <div className="fixed bottom-20 right-6 w-96">
          <Chatbot />
        </div>
      )}
    </>
  );
}
