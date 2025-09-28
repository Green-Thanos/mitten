'use client';
import React, { useState } from "react";
import domtoimage from 'dom-to-image-more';

interface ShareResultsModalProps {
  triggerText?: string;
  containerId: string;
}

const ShareResultsModal: React.FC<ShareResultsModalProps> = ({
  triggerText = "Share These Insights",
  containerId
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null);

  const handleOpenModal = async () => {
    const element = document.getElementById(containerId);
    if (!element) return;

    try {
      // Use dom-to-image-more to capture element
      const dataUrl = await domtoimage.toPng(element, {
        bgcolor: null, // keep transparency
        cacheBust: true, // avoids stale tiles
        width: element.scrollWidth,
        height: element.scrollHeight,
        style: {
          transform: 'scale(1)',
        },
      });
      setImageDataUrl(dataUrl);
      setModalOpen(true);
    } catch (err) {
      console.error("Error capturing image:", err);
    }
  };

  const handleDownload = () => {
    if (!imageDataUrl) return;
    const link = document.createElement("a");
    link.href = imageDataUrl;
    link.download = "enviducate-results.png";
    link.click();
  };

  const handleMobileShare = async () => {
    if (navigator.share && imageDataUrl) {
      try {
        const blob = await (await fetch(imageDataUrl)).blob();
        const filesArray = [new File([blob], "enviducate-results.png", { type: blob.type })];
        await navigator.share({
          files: filesArray,
          title: "Michigan Environmental Data - Enviducate",
        });
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <>

      <button
        onClick={handleOpenModal}
        className="w-full flex items-center gap-3 bg-green-500/20 hover:bg-green-500/30 text-green-300 rounded-lg p-3 transition-colors group"
      >
                      <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                viewBox="0 0 24 24"
              >
                <circle cx="18" cy="5" r="3" />
                <circle cx="6" cy="12" r="3" />
                <circle cx="18" cy="19" r="3" />
                <line x1="8.59" x2="15.42" y1="13.51" y2="17.49" />
                <line x1="15.41" x2="8.59" y1="6.51" y2="10.49" />
              </svg>
        <span>{triggerText}</span>
      </button>

      {modalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-black/90 p-6 rounded-2xl max-w-[90%] max-h-[90%] overflow-auto">
            <h2 className="text-white text-lg font-semibold mb-4">Share Preview</h2>
            {imageDataUrl && (
              <img
                src={imageDataUrl}
                alt="Share Preview"
                className="rounded-lg border border-white/20 mb-4 max-w-full"
              />
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
              >
                Close
              </button>
              <button
                onClick={handleDownload}
                className="px-4 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 transition-colors"
              >
                Download
              </button>
              {typeof navigator !== "undefined" && (
                <button
                  onClick={handleMobileShare}
                  className="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
                >
                  Share on Mobile
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ShareResultsModal;
