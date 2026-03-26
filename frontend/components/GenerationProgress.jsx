"use client";

/**
 * GenerationProgress
 *
 * Props (individual — matches how page.js passes them):
 *   stage, statusMessage, progress, sceneList, loading, onCancel
 */
export default function GenerationProgress({
  stage,
  statusMessage,
  progress,
  sceneList = [],
  loading,
  onCancel,
}) {
  const done = stage === "complete";

  if (!loading && !done) return null;

  return (
    <div className="w-full space-y-6">
      {/* ── Progress bar + status message ── */}
      <div className="glass-card p-6 flex flex-col gap-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-300">{statusMessage || "Starting…"}</span>
          <span className="text-gray-500 tabular-nums">{progress}%</span>
        </div>

        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Stage pills */}
        <div className="flex gap-2 flex-wrap">
          {STAGES.map(({ id, label }) => (
            <StagePill
              key={id}
              label={label}
              status={getPillStatus(id, stage, done)}
            />
          ))}
        </div>

        {/* Cancel button */}
        {loading && (
          <button
            onClick={onCancel}
            className="text-xs text-gray-600 hover:text-gray-400 transition-colors self-center mt-1"
          >
            Cancel
          </button>
        )}
      </div>

      {/* ── Scene thumbnail grid (populates live as images arrive) ── */}
      {sceneList.length > 0 && (
        <div className="glass-card p-6 flex flex-col gap-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider">
            Scenes — {sceneList.filter((s) => s.ready).length}/
            {sceneList.length} ready
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {sceneList.map((scene, i) => (
              <SceneCard key={i} index={i} scene={scene} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function SceneCard({ index, scene }) {
  return (
    <div className="relative rounded-lg overflow-hidden bg-white/5 border border-white/10 aspect-video">
      {scene.imageUrl ? (
        <img
          src={scene.imageUrl}
          alt={`Scene ${index + 1}`}
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <Spinner />
        </div>
      )}

      {/* Scene number */}
      <div className="absolute top-1.5 left-1.5 bg-black/60 rounded px-1.5 py-0.5 text-[10px] text-white/70">
        {index + 1}
      </div>

      {/* Subtitle */}
      {scene.subtitle && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1 text-[10px] text-white/80 truncate">
          {scene.subtitle}
        </div>
      )}
    </div>
  );
}

function StagePill({ label, status }) {
  const styles = {
    done: "bg-violet-500/20 text-violet-300 border border-violet-500/30",
    active:
      "bg-indigo-500/20 text-indigo-200 border border-indigo-400/40 animate-pulse",
    pending: "bg-white/5 text-white/30 border border-white/10",
  };
  return (
    <span
      className={`text-[11px] rounded-full px-2.5 py-0.5 ${styles[status]}`}
    >
      {status === "done" && "✓ "}
      {label}
    </span>
  );
}

function Spinner() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      className="animate-spin text-white/30"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <circle cx="12" cy="12" r="10" strokeOpacity=".2" />
      <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
    </svg>
  );
}

// ── Stage config ────────────────────────────────────────────────────────────

const STAGES = [
  { id: "analysing", label: "Analysing" },
  { id: "images", label: "Images" },
  { id: "voice", label: "Voiceover" },
  { id: "assembling", label: "Assembling" },
  { id: "complete", label: "Done" },
];

const STAGE_ORDER = STAGES.map((s) => s.id);

function getPillStatus(pillId, currentStage, done) {
  if (done) return "done";
  const pillIdx = STAGE_ORDER.indexOf(pillId);
  const currentIdx = STAGE_ORDER.indexOf(currentStage);
  if (pillIdx < currentIdx) return "done";
  if (pillIdx === currentIdx) return "active";
  return "pending";
}
