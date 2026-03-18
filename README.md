# 🎬 CineGen AI

**CineGen AI** is an end-to-end, AI-powered web application that transforms simple text scripts into fully synchronized, cinematic video slideshows. 

By leveraging advanced Large Language Models (LLMs) and diffusion image generation, the system intelligently splits your narrative into visual scenes, generates breathtaking imagery, creates voice narration, and stitches it all together with Hollywood-style camera effects and subtitles.

---

## ✨ Features

- **🧠 Intelligent Scene Direction**: Uses the **Groq API** (`llama-3.1-8b-instant`) to expand your short script into 5–7 rich, highly detailed cinematic scenes, automatically writing visual prompts and perfectly-timed subtitles.
- **🎨 AI Image Generation**: Uses the **Hugging Face Inference API** (`FLUX.1-schnell`) to generate gorgeous, high-resolution (1280x720) images matching your selected visual style (Cinematic, Anime, Realistic, Sci-Fi, etc.).
- **🗣️ Dynamic Narration**: Converts your scene subtitles into high-quality Text-to-Speech narration using **gTTS**.
- **🎥 Cinematic Stitching**: Uses **MoviePy** to assemble the final video, injecting:
  - **Ken Burns Effect**: Slow, continuous zoom on every image.
  - **Smooth Transitions**: 0.5s crossfades between scenes.
  - **Synced Timing**: Automatically guarantees the exact length of the video matches the narration audio track.
  - **Subtitles**: Clean, bottom-pinned visual subtitles matching the spoken dialogue.
  - **Background Music**: Auto-mixes ambient tracks (if provided) under the narration.
- **💻 Modern UI**: A sleek, dark-themed **Next.js 14** frontend with responsive glassmorphism design.

---

## 🏗️ Architecture

The application is split into a separated frontend and backend.

### Frontend (`/frontend`)
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS, PostCSS
- **Core Components**: 
  - `HeroSection` and `VideoPreview` (plays the final generated MP4 directly from the backend server)
  - `ScriptInput` and `StyleSelector`

### Backend (`/backend`)
- **Framework**: FastAPI, Uvicorn
- **AI Services**:
  - `services/scene_director.py`: Single-shot LLM orchestration (Groq).
  - `services/image_generator.py`: Text-to-image integration (HuggingFace).
  - `services/voice_generator.py`: Text-to-speech integration (gTTS).
  - `services/video_creator.py`: Video assembly, audio mixing, effects, rendering (MoviePy).
- **Video Serving**: Mounts FastAPI `StaticFiles` securely to serve the `outputs/final_video.mp4` locally to the frontend.

---

## 🚀 Getting Started

### Prerequisites
- Node.js & npm (for the frontend)
- Python 3.10+ (for the backend)
- API Keys:
  - **Groq API Key**: Get it [here](https://console.groq.com/keys)
  - **Hugging Face Token**: Get it [here](https://huggingface.co/settings/tokens)

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Install python dependencies
pip install -r requirements.txt

# Create a .env file and add your keys
echo "GROQ_API_KEY=your_groq_key" > .env
echo "HUGGINGFACE_API_KEY=your_hf_token" >> .env

# Start the FastAPI server
python -m uvicorn main:app --reload --port 8000
```

*The backend will be available at `http://localhost:8000`. You can view interactive API docs at `http://localhost:8000/docs`.*

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies (only needed once)
npm install

# Start the Next.js development server
npm run dev
```

*The frontend will be available at `http://localhost:3000`.*

---

## 🛠️ Usage

1. Open `http://localhost:3000` in your web browser.
2. Click **Start Generating**.
3. Type a creative script. For best results, use multiple sentences describing different visual actions.
   *Example: "A lone astronaut steps onto the dusty surface of Mars. A massive dust storm approaches on the horizon... "*
4. Select a **Visual Style** (e.g., Cinematic or Sci-Fi).
5. Click **Generate Video** and watch the terminal logs for progress. 
   *(Note: The first Hugging Face generation might take ~30s due to cold-starts).*
6. Watch, Download, or Share your finished video!

---

