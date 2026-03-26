"use client";
import { useState, useRef, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * useGeneration
 *
 * Handles the full generate → SSE-stream lifecycle.
 *
 * Returns:
 *   start(script, style)   — kick off generation
 *   cancel()               — close the SSE connection early
 *   state                  — current GenerationState object
 */
export function useGeneration() {
  const esRef = useRef(null); // EventSource reference

  const [state, setState] = useState(initialState());

  const updateState = (patch) => setState((prev) => ({ ...prev, ...patch }));

  // ── start ────────────────────────────────────────────────────────────────
  const start = useCallback(async (script, style) => {
    // Reset
    if (esRef.current) esRef.current.close();
    setState(initialState({ loading: true }));

    let jobId;
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script, style }),
      });
      if (!res.ok) throw new Error("Failed to start generation");
      ({ job_id: jobId } = await res.json());
    } catch (err) {
      updateState({ loading: false, error: err.message });
      return;
    }

    // ── Subscribe to SSE stream ──────────────────────────────────────────
    const es = new EventSource(`${API_BASE}/progress/${jobId}`);
    esRef.current = es;

    // status  — generic stage update
    es.addEventListener("status", (e) => {
      const d = JSON.parse(e.data);
      updateState({
        stage: d.stage,
        statusMessage: d.message,
        progress: d.progress,
      });
    });

    // scenes_ready  — LLM finished, we know how many scenes there are
    es.addEventListener("scenes_ready", (e) => {
      const d = JSON.parse(e.data);
      updateState({
        totalScenes: d.total,
        sceneList: d.scenes.map((s) => ({
          subtitle: s.subtitle,
          imageUrl: null,
          ready: false,
        })),
        statusMessage: `Script split into ${d.total} scenes`,
        progress: d.progress,
      });
    });

    // scene_image  — one image is done, show live thumbnail
    es.addEventListener("scene_image", (e) => {
      const d = JSON.parse(e.data);
      setState((prev) => {
        const sceneList = [...prev.sceneList];
        if (sceneList[d.index]) {
          sceneList[d.index] = {
            ...sceneList[d.index],
            imageUrl: d.image_b64
              ? `data:image/jpeg;base64,${d.image_b64}`
              : null,
            ready: true,
          };
        }
        return {
          ...prev,
          sceneList,
          progress: d.progress,
          statusMessage: d.message,
        };
      });
    });

    // complete  — video is ready
    es.addEventListener("complete", (e) => {
      const d = JSON.parse(e.data);
      updateState({
        loading: false,
        done: true,
        stage: "complete",
        statusMessage: d.message,
        progress: 100,
        downloadUrl: d.download_url,
      });
      es.close();
    });

    // error
    es.addEventListener("error", (e) => {
      let message = "An unexpected error occurred";
      try {
        message = JSON.parse(e.data).message;
      } catch {}
      updateState({ loading: false, error: message });
      es.close();
    });

    // Connection-level error (network drop, CORS, etc.)
    es.onerror = () => {
      updateState({
        loading: false,
        error: "Lost connection to server. Please try again.",
      });
      es.close();
    };
  }, []);

  // ── cancel ───────────────────────────────────────────────────────────────
  const cancel = useCallback(() => {
    if (esRef.current) esRef.current.close();
    setState(initialState());
  }, []);

  return { start, cancel, state };
}

// ── shape of generation state ─────────────────────────────────────────────
function initialState(overrides = {}) {
  return {
    loading: false,
    done: false,
    error: null,
    stage: "idle", // idle | analysing | images | voice | assembling | complete | error
    statusMessage: "",
    progress: 0, // 0–100
    totalScenes: 0,
    sceneList: [], // [{ subtitle, imageUrl, ready }]
    downloadUrl: null,
    ...overrides,
  };
}
