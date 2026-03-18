/*
  VideoPreview.jsx
  -----------------
  Shows the generated video from the real backend URL.

  Props:
    • videoUrl — full URL from FastAPI (http://localhost:8000/outputs/final_video.mp4)
    • script   — original script (shown as caption)
    • style    — selected style (shown as badge)
*/

export default function VideoPreview({ videoUrl, script, style }) {
    // A URL is "real" if it starts with http and comes from our backend
    const isReal = videoUrl && videoUrl.startsWith("http");

    // ── Download: create a hidden <a> pointing to the video URL ──────────────
    function handleDownload() {
        const link = document.createElement("a");
        link.href = videoUrl;
        link.download = "cinegen_video.mp4";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // ── Share: copy the video URL to clipboard ────────────────────────────────
    function handleShare() {
        navigator.clipboard
            .writeText(videoUrl)
            .then(() => alert("Video URL copied to clipboard!"))
            .catch(() => alert("Could not copy — your browser may not support it."));
    }

    return (
        <div className="glass-card overflow-hidden">

            {/* ── Header bar ── */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-[#2d2d3a]">
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-red-500/70" />
                    <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
                    <span className="w-3 h-3 rounded-full bg-green-500/70" />
                </div>
                <span className="text-xs text-gray-500">Generated Output</span>
                {style && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 capitalize">
                        {style}
                    </span>
                )}
            </div>

            {/* ── Video area ── */}
            {isReal ? (
                // Real video player using the backend URL
                <video
                    src={videoUrl}
                    controls
                    autoPlay
                    className="w-full aspect-video bg-black"
                />
            ) : (
                // Fallback if no URL yet
                <div className="relative w-full aspect-video bg-[#0d0d14] flex items-center justify-center">
                    <div
                        className="absolute inset-0"
                        style={{
                            background:
                                "linear-gradient(135deg, #1e1b4b 0%, #0f172a 40%, #134e4a 100%)",
                            opacity: 0.6,
                        }}
                    />
                    <div className="relative z-10 flex flex-col items-center gap-4 text-center px-6">
                        <div className="w-20 h-20 rounded-full bg-violet-500/20 border border-violet-400/30 flex items-center justify-center">
                            <span className="text-4xl">🎬</span>
                        </div>
                        <p className="text-white font-semibold text-lg">Video Ready! 🎉</p>
                    </div>
                </div>
            )}

            {/* ── Script caption ── */}
            {script && (
                <div className="px-5 py-4 border-t border-[#2d2d3a]">
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
                        Script used
                    </p>
                    <p className="text-sm text-gray-400 leading-relaxed line-clamp-3">
                        {script}
                    </p>
                </div>
            )}

            {/* ── Action buttons ── */}
            <div className="flex gap-3 px-5 pb-5">
                <button
                    onClick={handleDownload}
                    disabled={!isReal}
                    className="flex-1 py-2.5 rounded-lg text-sm font-semibold btn-gradient text-white disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    ⬇ Download
                </button>
                <button
                    onClick={handleShare}
                    disabled={!isReal}
                    className="flex-1 py-2.5 rounded-lg text-sm font-semibold border border-[#2d2d3a] text-gray-300 hover:border-violet-500 hover:text-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    🔗 Share
                </button>
            </div>
        </div>
    );
}
