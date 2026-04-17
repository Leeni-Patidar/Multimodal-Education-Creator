import { useState } from "react";
import InputForm from "./components/InputForm";
import TextOutput from "./components/TextOutput";
import ImageOutput from "./components/ImageOutput";
import History from "./components/History";

function App() {
  const [generatedData, setGeneratedData] = useState(null);
  const [showHistory, setShowHistory] = useState(true);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-screen-2xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <span className="text-blue-600">📚</span> Concept Visualizer AI
          </h1>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold text-sm transition"
          >
            {showHistory ? "Hide" : "Show"} History
          </button>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 bg-gray-50 overflow-hidden">
        <div className="h-full flex gap-6 px-6 py-6">
          
          {/* Left: Input */}
          <div className="w-1/4 min-h-0">
            <InputForm setData={setGeneratedData} />
          </div>

          {/* Middle: Text Output */}
          <div className="w-1/4 min-h-0">
            <TextOutput data={generatedData} />
          </div>

          {/* Right: Images */}
          <div className="w-1/4 min-h-0">
            <ImageOutput data={generatedData} />
          </div>

          {/* Far Right: History (Conditional) */}
          {showHistory && (
            <div className="w-1/4 min-h-0">
              <History />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;