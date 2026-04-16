import { useState } from "react";
import { generateContent } from "../api";

export default function InputForm({ setData }) {
  const [concept, setConcept] = useState("");
  const [outputType, setOutputType] = useState("Flashcard");
  const [imagePrompt, setImagePrompt] = useState("");
  const [imageStyle, setImageStyle] = useState("Photo-realistic");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [loading, setLoading] = useState(false);
  const [activeButton, setActiveButton] = useState(""); // 🔥 NEW

  const submitRequest = async (type) => {
    const topic = concept.trim();
    const refinedImagePrompt = imagePrompt.trim();

    if (!topic && !refinedImagePrompt) {
      return alert("Enter a concept or image prompt");
    }

    setLoading(true);

    try {
      const res = await generateContent({
        topic: topic || refinedImagePrompt,
        level: "basic",

        // 🔥 DIFFERENT behavior
        style:
          type === "visuals"
            ? imageStyle.toLowerCase()
            : "text",

        image_prompt: refinedImagePrompt || topic,
        image_count: type === "visuals" ? 5 : 0,
      });

      console.log("API Response:", res);

      setData({
        ...res,
        topic: res.topic || topic || refinedImagePrompt,
        outputType: type, // 🔥 important
      });
    } catch (err) {
      console.error("Error:", err);
      alert(
        "Error generating content: " +
          (err.response?.data?.error || err.message)
      );
    }

    setLoading(false);
  };

  const handleGenerateNarrative = async () => {
    setActiveButton("narrative");
    await submitRequest("narrative");
  };

  const handleGenerateVisuals = async () => {
    setActiveButton("visuals");
    await submitRequest("visuals");
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 border-b-4 border-blue-800">
        <h3 className="text-white font-bold text-lg">
          1. Define Concept & Prompts
        </h3>
      </div>

      <div className="p-6 space-y-6">
        {/* Concept */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Educational Concept
          </label>

          <textarea
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            placeholder="Enter a topic (e.g., Photosynthesis or Newton's Laws)"
            className="w-full h-20 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
        </div>

        {/* Narrative Button */}
        <button
          onClick={handleGenerateNarrative}
          disabled={loading || (!concept.trim() && !imagePrompt.trim())}
          className={`w-full py-2 rounded-lg font-medium transition text-white
            ${
              activeButton === "narrative"
                ? "bg-green-600"
                : "bg-blue-500 hover:bg-blue-600"
            }
            ${loading ? "opacity-70 cursor-not-allowed" : ""}
          `}
        >
          {loading && activeButton === "narrative"
            ? "Generating..."
            : "Generate Narrative"}
        </button>

        <div className="border-t-2 border-gray-200"></div>

        {/* Image Prompt */}
        <div>
          <h4 className="font-semibold text-gray-700 mb-3 text-sm">
            Refine Image Prompt
          </h4>

          <textarea
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
            placeholder="Describe visual scene..."
            className="w-full h-20 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm"
          />

          {/* Visual Button */}
          <button
            onClick={handleGenerateVisuals}
            disabled={loading || (!concept.trim() && !imagePrompt.trim())}
            className={`w-full py-2 rounded-lg font-medium mt-3 transition text-white
              ${
                activeButton === "visuals"
                  ? "bg-purple-600"
                  : "bg-blue-500 hover:bg-blue-600"
              }
              ${loading ? "opacity-70 cursor-not-allowed" : ""}
            `}
          >
            {loading && activeButton === "visuals"
              ? "Generating..."
              : "Generate Visuals"}
          </button>
        </div>
      </div>
    </div>
  );
}