import { useState } from "react";
import InputForm from "./components/InputForm";
import TextOutput from "./components/TextOutput";
import ImageOutput from "./components/ImageOutput";

function App() {
  const [generatedData, setGeneratedData] = useState(null);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-screen-2xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <span className="text-blue-600">📚</span> Concept Visualizer AI
          </h1>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 bg-gray-50 overflow-hidden">
        <div className="h-full max-w-screen-2xl mx-auto px-6 py-6 grid grid-cols-3 gap-6">
          
          {/* Left */}
          <div className="h-full min-h-0">
            <InputForm setData={setGeneratedData} />
          </div>

          {/* Middle */}
          <div className="h-full min-h-0">
            <TextOutput data={generatedData} />
          </div>

          {/* Right */}
          <div className="h-full min-h-0">
            <ImageOutput data={generatedData} />
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;