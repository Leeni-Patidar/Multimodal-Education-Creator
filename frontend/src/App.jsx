import { useState } from "react";
import InputForm from "./components/InputForm";
import TextOutput from "./components/TextOutput";
import ImageOutput from "./components/ImageOutput";
import History from "./components/History";

function App() {
  const [generatedData, setGeneratedData] = useState(null);
  const [showHistory, setShowHistory] = useState(true);
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);

  const handleReloadFromHistory = async (historyItem) => {
    // Trigger generation with the topic from history
    // The InputForm will receive this and populate its form
    setGeneratedData({
      topic: historyItem.topic,
      level: historyItem.level,
      isReloading: true,
      message: "Loading from history..."
    });

    // Import generateContent directly for the reload
    const { generateContent } = await import("./api");
    
    try {
      const payload = {
        topic: historyItem.topic,
        level: historyItem.level,
        style: "educational",
        image_prompt: historyItem.topic,
        image_count: 5
      };
      
      const result = await generateContent(payload);
      setGeneratedData(result);
      setHistoryRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error("Error reloading from history:", err);
      setGeneratedData({
        error: "Failed to reload content",
        topic: historyItem.topic
      });
    }
  };

  const handleDataGenerated = (newData) => {
    setGeneratedData(newData);
    setHistoryRefreshTrigger(prev => prev + 1);
  };

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
            <InputForm setData={handleDataGenerated} prefilledTopic={generatedData?.topic} />
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
              <History onReloadItem={handleReloadFromHistory} refreshTrigger={historyRefreshTrigger} />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;