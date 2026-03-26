"use client";

import { useState, useRef } from "react";
import ScriptInput from "@/components/ScriptInput";
import StyleSelector from "@/components/StyleSelector";
import GenerateButton from "@/components/GenerateButton";
import VideoPreview from "@/components/VideoPreview";
import GenerationProgress from "@/components/GenerationProgress";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function GeneratePage() {
    // ── Existing state (unchanged) ──────────────────────────────────
    const [script, setScript]   = useState("");
    const [style, setStyle]     = useState("cinematic");
    const [loading, setLoading] = useState(false);
    const [videoUrl, setVideoUrl] = useState(null);
    const [error, setError]     = useState(null);

    // ── New SSE progress state ──────────────────────────────────────
    const [progress, setProgress]         = useState(0);
    const [statusMessage, setStatusMessage] = useState("");
    const [stage, setStage]               = useState("idle");
    const [sceneList, setSceneList]       = useState([]);   // [{ subtitle, imageUrl, ready }]

    const esRef = useRef(null); // holds the EventSource so we can cancel it

    // ── Handle Generate button click ────────────────────────────────
    async function handleGenerate() {
        if (!script.trim()) {
            setError("Please enter a video script before generating.");
            return;
        }

        // Reset everything
        setError(null);
        setVideoUrl(null);
        setSceneList([]);
        setProgress(0);
        setStage("idle");
        setStatusMessage("");
        setLoading(true);

        // ── Step 1: POST to kick off the job, get back a job_id ─────
        let jobId;
        try {
            const res = await fetch(`${API_BASE}/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ script, style }),
            });
            if (!res.ok) throw new Error("Failed to start generation.");
            ({ job_id: jobId } = await res.json());
        } catch (err) {
            setError(err.message || "Could not reach the server.");
            setLoading(false);
            return;
        }

        // ── Step 2: Open SSE stream for live progress ───────────────
        const es = new EventSource(`${API_BASE}/progress/${jobId}`);
        esRef.current = es;

        // Generic stage / status updates
        es.addEventListener("status", (e) => {
            const d = JSON.parse(e.data);
            setStage(d.stage);
            setStatusMessage(d.message);
            setProgress(d.progress);
        });

        // LLM finished — we now know the scene list
        es.addEventListener("scenes_ready", (e) => {
            const d = JSON.parse(e.data);
            setSceneList(
                d.scenes.map((s) => ({ subtitle: s.subtitle, imageUrl: null, ready: false }))
            );
            setProgress(d.progress);
            setStatusMessage(`Script split into ${d.total} scenes`);
        });

        // One image is ready — update just that scene card
        es.addEventListener("scene_image", (e) => {
            const d = JSON.parse(e.data);
            setSceneList((prev) => {
                const updated = [...prev];
                if (updated[d.index]) {
                    updated[d.index] = {
                        ...updated[d.index],
                        imageUrl: d.image_b64
                            ? `data:image/jpeg;base64,${d.image_b64}`
                            : null,
                        ready: true,
                    };
                }
                return updated;
            });
            setProgress(d.progress);
            setStatusMessage(d.message);
        });

        // All done — show the video
        es.addEventListener("complete", (e) => {
            const d = JSON.parse(e.data);
            setProgress(100);
            setStage("complete");
            setStatusMessage(d.message);
            // Append cache-buster so the browser doesn't serve a stale file
            setVideoUrl(`${API_BASE}${d.download_url}?v=${Date.now()}`);
            setLoading(false);
            es.close();
        });

        // Server-sent error
        es.addEventListener("error", (e) => {
            let msg = "Generation failed. Please try again.";
            try { msg = JSON.parse(e.data).message; } catch {}
            setError(msg);
            setLoading(false);
            es.close();
        });

        // Network / connection error
        es.onerror = () => {
            setError("Lost connection to server. Please try again.");
            setLoading(false);
            es.close();
        };
    }

    // ── Cancel mid-generation ───────────────────────────────────────
    function handleCancel() {
        if (esRef.current) esRef.current.close();
        setLoading(false);
        setStage("idle");
        setStatusMessage("");
        setProgress(0);
    }

    return (
        <div className="min-h-screen pt-24 pb-16 px-4">
            <div className="max-w-3xl mx-auto flex flex-col gap-8">

                {/* ── Page Header ── */}
                <div className="text-center">
                    <h1 className="text-4xl md:text-5xl font-extrabold gradient-text">
                        Generate a Video
                    </h1>
                    <p className="text-gray-400 mt-3 text-base md:text-lg">
                        Describe your scene, pick a style, and watch the magic happen.
                    </p>
                </div>

                {/* ── Input Card ── */}
                <div className="glass-card p-6 md:p-8 flex flex-col gap-7">
                    <ScriptInput value={script} onChange={setScript} />

                    <div className="border-t border-[#2d2d3a]" />

                    <StyleSelector selectedStyle={style} onSelect={setStyle} />

                    {error && (
                        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                            <span>⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    <GenerateButton onClick={handleGenerate} disabled={loading} />
                </div>

                {/* ── Live Progress UI (replaces the old <Loader />) ── */}
                {(loading || stage === "complete") && (
                    <GenerationProgress
                        stage={stage}
                        statusMessage={statusMessage}
                        progress={progress}
                        sceneList={sceneList}
                        onCancel={handleCancel}
                        loading={loading}
                    />
                )}

                {/* ── Video preview — same as before ── */}
                {videoUrl && !loading && (
                    <VideoPreview
                        videoUrl={videoUrl}
                        script={script}
                        style={style}
                    />
                )}

            </div>
        </div>
    );
}
