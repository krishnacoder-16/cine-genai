/*
  app/generate/page.js  (route: "/generate")
  -------------------------------------------
  This is the BRAIN of the generate feature.

  ── WHY all state lives HERE (lifted state) ──
  React data flows one way: parent → child via props.
  All components on this page (ScriptInput, StyleSelector etc.)
  need to share the same data, so we store it in ONE place — here.
  Each child gets what it needs as a prop.

  ── State variables ──
  • script    → what the user typed in the textarea
  • style     → which visual style card they selected
  • loading   → true while the mock API call is running
  • videoUrl  → the result URL once generation is "done"

  ── Flow ──
  User types → script state updates
  User picks style → style state updates
  User clicks Generate:
    1. loading = true   (shows <Loader />)
    2. calls generateVideo() from utils/api.js (waits 3 seconds)
    3. loading = false, videoUrl = result  (shows <VideoPreview />)
*/

"use client"; // ← needed because we use useState and handle events

import { useState } from "react";
import ScriptInput from "@/components/ScriptInput";
import StyleSelector from "@/components/StyleSelector";
import GenerateButton from "@/components/GenerateButton";
import Loader from "@/components/Loader";
import VideoPreview from "@/components/VideoPreview";
import { generateVideo } from "@/utils/api";

export default function GeneratePage() {
    // ── All state lives here (lifted) ──────────────────────────────
    const [script, setScript] = useState("");          // user's prompt text
    const [style, setStyle] = useState("cinematic"); // default style
    const [loading, setLoading] = useState(false);       // is API call in flight?
    const [videoUrl, setVideoUrl] = useState(null);        // result from API
    const [error, setError] = useState(null);        // any error message

    // ── Handle the Generate button click ───────────────────────────
    async function handleGenerate() {
        // Guard: don't generate if script is empty
        if (!script.trim()) {
            setError("Please enter a video script before generating.");
            return;
        }

        // Reset previous results and start loading
        setError(null);
        setVideoUrl(null);
        setLoading(true);

        try {
            // Call the real FastAPI backend via utils/api.js
            const data = await generateVideo({ script, style });
            // data.video_url comes from the backend response
            setVideoUrl(data.video_url);
        } catch (err) {
            // Show the actual error message from the API (or a fallback)
            setError(err.message || "Something went wrong. Please try again.");
        } finally {
            // Always stop the loader, whether success or error
            setLoading(false);
        }
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

                    {/* 1. Script input — value and setter passed as props */}
                    <ScriptInput
                        value={script}
                        onChange={setScript}
                    />

                    {/* Divider */}
                    <div className="border-t border-[#2d2d3a]" />

                    {/* 2. Style selector — selected value and setter passed as props */}
                    <StyleSelector
                        selectedStyle={style}
                        onSelect={setStyle}
                    />

                    {/* Error message (shown if script is empty or API fails) */}
                    {error && (
                        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                            <span>⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* 3. Generate button — disabled while loading */}
                    <GenerateButton
                        onClick={handleGenerate}
                        disabled={loading}
                    />
                </div>

                {/* ── Output Area ── */}
                {/* Show Loader while generating, VideoPreview once done */}
                {loading && <Loader />}

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
