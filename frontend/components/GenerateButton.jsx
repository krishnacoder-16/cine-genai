/*
  GenerateButton.jsx
  -------------------
  The main CTA button that kicks off video generation.

  Props:
    • onClick   — function to call when button is clicked
    • disabled  — boolean; true while a video is loading
                  (prevents double-clicks and shows different text)
*/

export default function GenerateButton({ onClick, disabled }) {
    return (
        <button
            type="button"
            onClick={onClick}
            disabled={disabled}
            className={`
        w-full py-4 rounded-xl font-bold text-base tracking-wide
        transition-all duration-200
        ${disabled
                    ? // While generating: greyed out, no hover effects, not-allowed cursor
                    "bg-violet-800/40 text-violet-400/60 cursor-not-allowed"
                    : // Ready: full gradient with hover glow + lift
                    "btn-gradient text-white shadow-lg hover:shadow-violet-500/40 active:scale-[0.98]"
                }
      `}
        >
            {disabled ? (
                // Animated dots to indicate work is happening
                <span className="flex items-center justify-center gap-2">
                    <span
                        className="w-2 h-2 rounded-full bg-violet-400 animate-bounce"
                        style={{ animationDelay: "0ms" }}
                    />
                    <span
                        className="w-2 h-2 rounded-full bg-violet-400 animate-bounce"
                        style={{ animationDelay: "150ms" }}
                    />
                    <span
                        className="w-2 h-2 rounded-full bg-violet-400 animate-bounce"
                        style={{ animationDelay: "300ms" }}
                    />
                    <span className="ml-1">Generating your video…</span>
                </span>
            ) : (
                "🎬 Generate Video"
            )}
        </button>
    );
}
