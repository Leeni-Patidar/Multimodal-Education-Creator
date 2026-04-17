import { useState, useEffect } from "react";
import { getHistory, searchHistory } from "../api";

export default function History({ onReloadItem, refreshTrigger }) {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [reloadingId, setReloadingId] = useState(null);

  // 🔹 Helper: Sort latest first
  const sortByLatest = (data) => {
    return (data || []).sort(
      (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
    );
  };

  // Load history on component mount and when refreshTrigger changes
  useEffect(() => {
    loadHistory();
  }, [refreshTrigger]);

  const loadHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getHistory(15);
      setHistory(sortByLatest(data.history));
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
      setHistory(sortByLatest(data.history));
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

  const handleReloadItem = async (item) => {
    if (!onReloadItem) return;
    
    setReloadingId(item.id);
    try {
      await onReloadItem({
        topic: item.topic,
        level: item.level,
        content_preview: item.content_preview
      });
    } catch (err) {
      console.error("Error reloading item:", err);
      setError("Failed to reload item");
    } finally {
      setReloadingId(null);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 border-b-4 border-purple-800">
        <h3 className="text-white font-bold text-lg">📋 Generation History</h3>
        
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
              onClick={() => handleReloadItem(item)}
            >
              {/* Topic */}
              {item.topic && (
                <div className="text-xs text-gray-600 mb-2 truncate">
                  <strong>Topic:</strong> {item.topic}
                </div>
              )}



              {/* Timestamp */}
              {item.timestamp && (
                <div className="text-xs text-gray-500 italic">
                  {new Date(item.timestamp).toLocaleDateString()}{" "}
                  {new Date(item.timestamp).toLocaleTimeString()}
                </div>
              )}

              {/* Content Preview */}
              {item.content_preview && (
                <div className="mt-2 text-xs text-gray-600 italic line-clamp-2 bg-white bg-opacity-50 p-2 rounded">
                  "{item.content_preview}"
                </div>
              )}

              {/* Reload Indicator */}
              {reloadingId === item.id && (
                <div className="mt-2 text-xs text-center text-purple-600 font-semibold">
                  ⟳ Reloading...
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