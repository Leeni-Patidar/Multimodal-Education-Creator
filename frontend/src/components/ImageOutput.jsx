import { useState } from "react";

export default function ImageOutput({ data }) {
  const [selectedImage, setSelectedImage] = useState(0);
  const [showModal, setShowModal] = useState(false);

  const images = data?.images || (data?.image ? [data.image] : []);

  return (
    <>
      <div className="bg-white rounded-xl shadow-md overflow-hidden h-full flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-orange-700 px-6 py-4 border-b-4 border-orange-800">
          <h3 className="text-white font-bold text-lg">3. Generate Image Output</h3>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 flex flex-col">
          {data && images.length > 0 ? (
            <div className="space-y-4 flex-1 flex flex-col">
              
              {/* Main Image (SMALLER SIZE) */}
              <div className="flex-1 flex items-center justify-center">
                <div className="w-[300px] h-[300px] rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-100 flex items-center justify-center">
                  <img
                    src={
                      typeof images[selectedImage] === "string" &&
                      images[selectedImage].startsWith("data:")
                        ? images[selectedImage]
                        : `data:image/png;base64,${images[selectedImage]}`
                    }
                    alt={`Generated ${selectedImage + 1}`}
                    className="w-full h-full object-contain cursor-pointer hover:scale-105 transition"
                    onClick={() => setShowModal(true)}
                  />
                </div>
              </div>

              {/* Thumbnails */}
              {images.length > 1 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2 text-sm">
                    Generated Variations
                  </h4>
                  <div className="grid grid-cols-3 gap-2">
                    {images.map((image, idx) => (
                      <div
                        key={idx}
                        onClick={() => setSelectedImage(idx)}
                        className={`cursor-pointer rounded-lg overflow-hidden border-2 transition ${
                          selectedImage === idx
                            ? "border-orange-600 shadow-lg"
                            : "border-gray-200 hover:border-orange-400"
                        }`}
                      >
                        <img
                          src={
                            typeof image === "string" && image.startsWith("data:")
                              ? image
                              : `data:image/png;base64,${image}`
                          }
                          alt={`Variation ${idx + 1}`}
                          className="w-full h-20 object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center flex-1 text-gray-400">
              <div className="text-center">
                <p className="text-lg mb-2">🖼️</p>
                <p className="text-sm">
                  Generated images will appear here after clicking "Generate Visuals"
                </p>
                {data && !images.length && (
                  <p className="text-xs mt-2 text-red-500">
                    Error: No image in response
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 🔥 MODAL POPUP */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          
          {/* Background Blur */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setShowModal(false)}
          ></div>

          {/* Center Image */}
          <div className="relative z-10 max-w-3xl w-full p-4">
            <img
              src={
                typeof images[selectedImage] === "string" &&
                images[selectedImage].startsWith("data:")
                  ? images[selectedImage]
                  : `data:image/png;base64,${images[selectedImage]}`
              }
              alt="Preview"
              className="w-full max-h-[80vh] object-contain rounded-lg shadow-xl"
            />

            {/* Close Button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-2 right-2 bg-white text-black px-3 py-1 rounded-full shadow hover:bg-gray-200"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </>
  );
}