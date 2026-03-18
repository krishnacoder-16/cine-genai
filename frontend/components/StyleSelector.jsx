/*
  StyleSelector.jsx
  ------------------
  A row of clickable style cards. The user picks ONE style.

  "Controlled" means:
    - `selectedStyle` comes from the parent as a prop
    - Clicking a card fires `onSelect(styleName)` to update parent state
    - This component never owns any state itself

  Props:
    • selectedStyle — the currently active style (string, from parent)
    • onSelect      — function called with the style name when a card is clicked
*/

// The list of available styles with an emoji icon + short description
const STYLES = [
    {
        id: "cinematic",
        label: "Cinematic",
        icon: "🎬",
        desc: "Hollywood-quality dramatic shots",
    },
    {
        id: "anime",
        label: "Anime",
        icon: "⛩️",
        desc: "Japanese animated style",
    },
    {
        id: "realistic",
        label: "Realistic",
        icon: "📷",
        desc: "Photorealistic and lifelike",
    },
    {
        id: "abstract",
        label: "Abstract",
        icon: "🌀",
        desc: "Surreal and artistic visuals",
    },
    {
        id: "retro",
        label: "Retro",
        icon: "📼",
        desc: "80s/90s vintage aesthetic",
    },
    {
        id: "scifi",
        label: "Sci-Fi",
        icon: "🚀",
        desc: "Futuristic space & tech vibes",
    },
];

export default function StyleSelector({ selectedStyle, onSelect }) {
    return (
        <div className="flex flex-col gap-3">
            {/* Label */}
            <label className="text-sm font-semibold text-gray-300 tracking-wide uppercase">
                🎨 Visual Style
            </label>
            <p className="text-xs text-gray-500 -mt-2">
                Choose the look and feel of your generated video.
            </p>

            {/* Style cards grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {STYLES.map((style) => {
                    const isSelected = selectedStyle === style.id;

                    return (
                        <button
                            key={style.id}
                            type="button"
                            onClick={() => onSelect(style.id)}
                            className={`
                flex flex-col items-start gap-1 p-4 rounded-xl border text-left
                transition-all duration-200 cursor-pointer
                ${isSelected
                                    ? // Selected: glowing purple border + subtle purple bg
                                    "border-violet-500 bg-violet-500/10 shadow-[0_0_12px_rgba(124,58,237,0.3)]"
                                    : // Not selected: muted border, hover effect
                                    "border-[#2d2d3a] bg-[#13131a] hover:border-violet-500/50 hover:bg-violet-500/5"
                                }
              `}
                        >
                            <span className="text-2xl">{style.icon}</span>
                            <span
                                className={`text-sm font-semibold ${isSelected ? "text-violet-300" : "text-gray-300"
                                    }`}
                            >
                                {style.label}
                            </span>
                            <span className="text-xs text-gray-500 leading-snug">
                                {style.desc}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
