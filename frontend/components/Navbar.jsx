/*
  Navbar.jsx  (components/Navbar.jsx)
  ------------------------------------
  The top navigation bar visible on EVERY page.

  Features:
    • Logo "CineGen AI" with gradient colour
    • Navigation links: Home, Generate, Pricing
    • Sticky position so it stays at the top on scroll
    • Glass/blur effect for a premium dark-theme look
    • Hamburger menu placeholder comment for future mobile support
*/

"use client"; // ← needed because we use React state for the mobile menu

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
    // Controls whether the mobile dropdown menu is open
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <nav
            className="
        fixed top-0 left-0 right-0 z-50
        flex items-center justify-between
        px-6 py-4
        backdrop-blur-md
        border-b border-[#2d2d3a]
      "
            style={{ background: "rgba(10, 10, 15, 0.85)" }}
        >
            {/* ── Logo ── */}
            <Link href="/" className="flex items-center gap-2">
                {/* Simple emoji clapperboard as a logo icon — replace with an SVG later */}
                <span className="text-2xl">🎬</span>
                <span className="text-xl font-bold gradient-text">CineGen AI</span>
            </Link>

            {/* ── Desktop Navigation Links ── */}
            <ul className="hidden md:flex items-center gap-8 text-sm font-medium">
                <li>
                    <Link
                        href="/"
                        className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                        Home
                    </Link>
                </li>
                <li>
                    <Link
                        href="/generate"
                        className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                        Generate
                    </Link>
                </li>
            </ul>


            {/* ── Mobile Hamburger Button ── */}
            <button
                className="md:hidden text-gray-400 hover:text-white"
                onClick={() => setMenuOpen(!menuOpen)}
                aria-label="Toggle menu"
            >
                {/* Three horizontal bars = hamburger icon */}
                <div className="space-y-1.5">
                    <span className="block w-6 h-0.5 bg-current"></span>
                    <span className="block w-6 h-0.5 bg-current"></span>
                    <span className="block w-6 h-0.5 bg-current"></span>
                </div>
            </button>

            {/* ── Mobile Dropdown Menu ── */}
            {menuOpen && (
                <div
                    className="
            absolute top-full left-0 right-0
            glass-card rounded-none border-t-0
            flex flex-col gap-4 px-6 py-5
            md:hidden
          "
                >
                    <Link href="/" className="text-gray-300 hover:text-white" onClick={() => setMenuOpen(false)}>Home</Link>
                    <Link href="/generate" className="text-gray-300 hover:text-white" onClick={() => setMenuOpen(false)}>Generate</Link>

                </div>
            )}
        </nav>
    );
}
