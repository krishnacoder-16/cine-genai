/*
  layout.js  (app/layout.js)
  --------------------------
  This is the ROOT LAYOUT — Next.js wraps EVERY page with this file.
  Think of it like a picture frame: whatever is here appears on all pages.

  Responsibilities:
    • Sets the <html> and <body> tags
    • Imports global CSS (so Tailwind works everywhere)
    • Renders <Navbar /> at the top of every page
    • `children` is the actual page content that changes per route
*/

import "./globals.css";
import Navbar from "@/components/Navbar";

// This metadata object sets the browser tab title and description automatically
export const metadata = {
    title: "CineGen AI — Turn Ideas Into Cinema",
    description:
        "AI-powered video generation. Type a prompt, pick a style, get a cinematic video.",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>
                {/* Navbar is rendered once here, so it appears on every page */}
                <Navbar />

                {/* Main content area — each page fills this */}
                <main>{children}</main>
            </body>
        </html>
    );
}
