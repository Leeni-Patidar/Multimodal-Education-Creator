import { useState, useEffect } from "react";
import { getHistory, searchHistory } from "../api";

export default function History() {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  // Load history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getHistory(15);
      setHistory(data.history || []);
      setHasSearched(false);
    } catch (err) {
      console.error("Error loading history:", err);
      setError("Failed to load history");
      setHistory([]);
    }
    setLoading(false);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      loadHistory();
      return;
    }

    setLoading(true);
    setError("");
    setHasSearched(true);

    try {
      const data = await searchHistory(
        searchQuery,
        "",
        selectedLevel,
        15
      );
      setHistory(data.history || []);
    } catch (err) {
      console.error("Error searching history:", err);
      setError("Failed to search history");
      setHistory([]);
    }
    setLoading(false);
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    setSelectedLevel("");
    setHasSearched(false);
    loadHistory();
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 border-b-4 border-purple-800">
        <h3 className="text-white font-bold text-lg">📋 Generation History</h3>
        <p className="text-purple-100 text-sm mt-1">Search your past generations</p>
      </div>

      {/* Search Section */}
      <div className="p-4 bg-purple-50 border-b border-purple-200">
        <form onSubmit={handleSearch} className="space-y-3">
          {/* Search Input */}
          <div>
            <input
              type="text"
              placeholder="Search by topic..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
            />
          </div>


          {/* Buttons */}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition text-sm"
            >
              {loading ? "Searching..." : "Search"}
            </button>
            {hasSearched && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 rounded-lg transition text-sm"
              >
                Clear
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* History Items */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading && !history.length ? (
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500 text-sm">Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500 text-sm">No history found</p>
          </div>
        ) : (
          history.map((item, idx) => (
            <div
              key={item.id || idx}
              className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-500 rounded-lg hover:shadow-md transition cursor-pointer"
            >
              {/* Title */}


              {/* Topic/Query */}
              {item.topic && (
                <div className="text-xs text-gray-600 mb-2 truncate">
                  <strong>Topic:</strong> {item.topic}
                </div>
              )}


              {/* Timestamp */}
              {item.timestamp && (
                <div className="text-xs text-gray-500 italic">
                  {new Date(item.timestamp).toLocaleDateString()} {new Date(item.timestamp).toLocaleTimeString()}
                </div>
              )}

              {/* Content Preview */}
              {item.content_preview && (
                <div className="mt-2 text-xs text-gray-600 italic line-clamp-2 bg-white bg-opacity-50 p-2 rounded">
                  "{item.content_preview}"
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer Info */}
      {history.length > 0 && (
        <div className="p-3 bg-purple-100 text-purple-700 text-center text-xs font-semibold border-t border-purple-200">
          Showing {history.length} items
        </div>
      )}
    </div>
  );
}
