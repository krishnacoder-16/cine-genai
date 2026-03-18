/** @type {import('tailwindcss').Config} */
module.exports = {
    // Tell Tailwind where to look for class names so unused CSS is removed in production
    content: [
        "./app/**/*.{js,jsx}",
        "./components/**/*.{js,jsx}",
        "./pages/**/*.{js,jsx}",
    ],
    theme: {
        extend: {
            // Custom brand colours for CineGen AI
            colors: {
                brand: {
                    purple: "#7c3aed",   // primary accent
                    violet: "#a78bfa",   // lighter accent
                    dark: "#0a0a0f",   // deep background
                    card: "#13131a",   // card/section background
                    border: "#2d2d3a",   // subtle borders
                },
            },
            // Custom gradient used on headlines and buttons
            backgroundImage: {
                "brand-gradient":
                    "linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #06b6d4 100%)",
            },
            fontFamily: {
                sans: ["Inter", "sans-serif"],
            },
        },
    },
    plugins: [],
};
