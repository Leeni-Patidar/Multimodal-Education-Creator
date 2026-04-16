// Parse markdown bold formatting (**text**) to React elements
const parseMarkdownBold = (text) => {
  if (!text) return "";

  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, idx) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={idx} className="font-bold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <span key={idx}>{part}</span>;
  });
};

export default function TextOutput({ data }) {
  return (
    <div className="bg-white rounded-xl shadow-md h-full flex flex-col overflow-hidden">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 border-b-4 border-green-800 shrink-0">
        <h3 className="text-white font-bold text-lg">
          2. Generate Text Output
        </h3>
      </div>

      {/* Content */}
      <div className="p-6 flex-1 flex flex-col overflow-hidden min-h-0">
        {data ? (
          <div className="space-y-4 flex-1 flex flex-col min-h-0">
            
            {/* Topic */}
           <div className="shrink-0">
              <h4 className="font-semibold text-gray-800 mb-2 text-sm">
                Topic
              </h4>
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                <p className="text-gray-700 font-medium">
                  {data.topic
                    ? data.topic.charAt(0).toUpperCase() + data.topic.slice(1).toLowerCase()
                    : "N/A"}
                </p>
              </div>
            </div>

            {/* Text Explanation */}
            <div className="flex-1 flex flex-col min-h-0">
              <h4 className="font-semibold text-gray-800 mb-2 text-sm shrink-0">
                Text Explanation
              </h4>

              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 flex-1 overflow-y-auto min-h-0">
                <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {parseMarkdownBold(
                    data.explanation || "No text explanation available"
                  )}
                </div>
              </div>
            </div>

          </div>
        ) : (
          <div className="flex items-center justify-center flex-1 text-gray-400">
            <div className="text-center">
              <p className="text-lg mb-2">📝</p>
              <p className="text-sm">
                Generate text by entering a concept and clicking "Generate Narrative"
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}