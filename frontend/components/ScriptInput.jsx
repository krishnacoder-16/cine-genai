/*
  ScriptInput.jsx
  ---------------
  A CONTROLLED textarea for the user's video script/prompt.

  "Controlled" means:
    - The value always comes from the parent via the `value` prop
    - When the user types, it calls `onChange` to tell the parent
    - The parent (generate/page.js) holds the actual state

  Props:
    • value    — the current script text (from parent state)
    • onChange — function called whenever the user types
*/

export default function ScriptInput({ value, onChange }) {
    return (
        <div className="flex flex-col gap-2">
            {/* Label */}
            <label
                htmlFor="script-input"
                className="text-sm font-semibold text-gray-300 tracking-wide uppercase"
            >
                ✍️ Your Video Script
            </label>

            {/* Hint text */}
            <p className="text-xs text-gray-500 -mt-1">
                Describe the scene, mood, and story. More detail = better video.
            </p>

            {/* Textarea */}
            <textarea
                id="script-input"
                rows={6}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="e.g. A lone astronaut walks across a red Martian desert at sunset, dust swirling around their boots..."
                className="
          w-full rounded-xl px-4 py-3
          bg-[#13131a] border border-[#2d2d3a]
          text-gray-200 placeholder-gray-600
          text-sm leading-relaxed resize-none
          focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/40
          transition-colors duration-200
        "
            />

            {/* Character counter */}
            <p className="text-xs text-gray-600 text-right">
                {value.length} / 500 characters
            </p>
        </div>
    );
}
