/*
  HeroSection.jsx  (components/HeroSection.jsx)
  -----------------------------------------------
  The big eye-catching section shown on the Home page.

  What it contains:
    • A badge label ("AI-Powered Video Generation")
    • A large bold headline with gradient text
    • A supporting sub-headline
    • Two CTA buttons: primary "Start Generating" + secondary "Watch Demo"
    • Animated floating gradient orbs in the background
    • A mock "preview card" showing what a generated video looks like
*/

"use client";

import Link from "next/link";


export default function HeroSection() {
    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 overflow-hidden text-center">

            {/* ── Background decorative orbs (pure CSS animations) ── */}
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 overflow-hidden"
            >
                {/* Top-left purple orb */}
                <div
                    className="absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-30 blur-3xl animate-pulse"
                    style={{ background: "radial-gradient(circle, #7c3aed, transparent)" }}
                />
                {/* Bottom-right cyan orb */}
                <div
                    className="absolute -bottom-32 -right-32 w-80 h-80 rounded-full opacity-20 blur-3xl animate-pulse"
                    style={{
                        background: "radial-gradient(circle, #06b6d4, transparent)",
                        animationDelay: "1s",
                    }}
                />
                {/* Centre indigo orb */}
                <div
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full opacity-10 blur-3xl"
                    style={{ background: "radial-gradient(circle, #6366f1, transparent)" }}
                />
            </div>

            {/* ── Content (sits above the orbs) ── */}
            <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center gap-6">

                {/* Badge */}
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#7c3aed]/40 bg-[#7c3aed]/10 text-violet-300 text-sm font-medium">
                    <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse inline-block" />
                    AI-Powered Video Generation
                </div>

                {/* Headline */}
                <h1 className="text-5xl md:text-7xl font-extrabold leading-tight tracking-tight">
                    Turn Your Ideas Into{" "}
                    <span className="gradient-text">Cinematic Videos</span>
                </h1>

                {/* Sub-headline */}
                <p className="text-lg md:text-xl text-gray-400 max-w-2xl leading-relaxed">
                    Type a script, choose a visual style, and let CineGen AI produce a
                    stunning video in seconds — no editing skills required.
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row items-center gap-4 mt-2">
                    <Link
                        href="/generate"
                        className="btn-gradient text-white font-semibold px-8 py-3.5 rounded-full text-base shadow-lg"
                    >
                        Start Generating →
                    </Link>
                </div>

                {/* ── Video Preview Card ── */}
                <div className="mt-12 glass-card p-1 w-full max-w-3xl shadow-2xl shadow-violet-900/20">
                    {/* Browser-chrome bar */}
                    <div className="flex items-center gap-2 px-4 py-3 border-b border-[#2d2d3a]">
                        <span className="w-3 h-3 rounded-full bg-red-500/70" />
                        <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
                        <span className="w-3 h-3 rounded-full bg-green-500/70" />
                        <span className="ml-4 text-xs text-gray-500">cinegen.ai/generate</span>
                    </div>

                    {/* Real video player — plays the last generated video */}
                    <video
                        src="http://localhost:8000/outputs/final_video.mp4"
                        controls
                        className="w-full aspect-video rounded-b-xl bg-black"
                        onError={(e) => {
                            // If no video exists yet, swap in a placeholder
                            e.target.style.display = "none";
                            e.target.nextSibling.style.display = "flex";
                        }}
                    />
                    {/* Fallback shown only when video hasn't been generated yet */}
                    <div
                        className="w-full aspect-video rounded-b-xl bg-[#0d0d14] items-center justify-center flex-col gap-3"
                        style={{ display: "none" }}
                    >
                        <div className="w-16 h-16 rounded-full bg-white/10 border border-white/20 flex items-center justify-center">
                            <span className="text-2xl ml-1">▶</span>
                        </div>
                        <p className="text-gray-400 text-sm">Your video preview will appear here</p>
                    </div>
                </div>


            </div>
        </section>
    );
}
