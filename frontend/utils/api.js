/*
  utils/api.js
  ------------
  Calls the real FastAPI backend at http://localhost:8000/generate-video.

  Sends:   { script, style }
  Returns: the full parsed JSON response — caller uses response.video_url
*/

// The backend URL — change this when deploying to production
const API_BASE = "http://localhost:8000";

export async function generateVideo({ script, style }) {
  // Call the FastAPI endpoint
  const res = await fetch(`${API_BASE}/generate-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ script, style }),
  });

  // If the server returned a non-2xx status (4xx / 5xx), throw an error
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${res.status}`);
  }

  // Parse and return the JSON response
  // Shape: { success: boolean, video_url: string, message: string }
  const data = await res.json();

  // If the backend returned success: false, treat it as an error
  if (!data.success) {
    throw new Error(data.message || "Generation failed.");
  }

  return data;
}
