/*
  Loader.jsx
  -----------
  A full-width animated loading card shown while the video is being generated.
  This replaces the <VideoPreview /> area while `loading` is true in the parent.

  No props needed — it's purely decorative.
  The parent decides WHEN to show it (based on the `loading` state).
*/

export default function Loader() {
    return (
        <div className="glass-card flex flex-col items-center justify-center gap-6 py-16 px-8 text-center">

            {/* Spinning ring */}
            <div className="relative w-16 h-16">
                {/* Outer ring (spins) */}
                <div className="absolute inset-0 rounded-full border-4 border-violet-500/20" />
                <div
                    className="absolute inset-0 rounded-full border-4 border-transparent border-t-violet-500 animate-spin"
                    style={{ animationDuration: "0.9s" }}
                />
                {/* Centre dot */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-3 h-3 rounded-full bg-violet-400 animate-pulse" />
                </div>
            </div>

            {/* Text */}
            <div className="flex flex-col gap-1">
                <p className="text-white font-semibold text-lg">
                    Generating your video…
                </p>
                <p className="text-gray-500 text-sm">
                    Our AI is crafting your cinematic scene. This usually takes 15–30 seconds.
                </p>
            </div>

            {/* Progress bar (animated shimmer — purely visual) */}
            <div className="w-full max-w-xs h-1.5 rounded-full bg-[#2d2d3a] overflow-hidden">
                <div
                    className="h-full rounded-full bg-brand-gradient animate-pulse"
                    style={{
                        background: "linear-gradient(90deg, #7c3aed, #6366f1, #06b6d4)",
                        width: "60%",
                    }}
                />
            </div>
        </div>
    );
}
