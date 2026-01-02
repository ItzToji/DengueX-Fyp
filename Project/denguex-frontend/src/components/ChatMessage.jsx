export default function ChatMessage({ role, text }) {
  const isUser = role === "user";

  return (
    <div className={`my-2 flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`px-4 py-2 rounded-lg max-w-lg ${
          isUser ? "bg-indigo-600 text-white" : "bg-gray-200 text-black"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
