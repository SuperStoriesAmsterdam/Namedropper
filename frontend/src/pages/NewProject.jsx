import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useApi } from "../hooks/useApi";

const STEPS = ["Upload files", "Set pause point", "Add names", "Review"];

export default function NewProject() {
  const [step, setStep] = useState(0);
  // Voice sample
  const [voiceFile, setVoiceFile] = useState(null);
  const [voiceUrl, setVoiceUrl] = useState("");
  // Video
  const [videoFile, setVideoFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [videoPreviewUrl, setVideoPreviewUrl] = useState("");
  // Other state
  const [pauseSeconds, setPauseSeconds] = useState("");
  const [title, setTitle] = useState("");
  const [namesText, setNamesText] = useState("");
  const [cleanedNames, setCleanedNames] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const { apiFetch } = useApi();
  const navigate = useNavigate();

  // ── Step 1: Upload voice sample + video ───────────────────

  function handleVoiceSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    setError("");

    if (file.size > 10 * 1024 * 1024) {
      setError("Voice sample exceeds the 10 MB limit.");
      return;
    }

    const validTypes = [
      "audio/mpeg",
      "audio/wav",
      "audio/mp4",
      "audio/x-m4a",
      "audio/ogg",
      "audio/webm",
    ];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|ogg|webm)$/i)) {
      setError("Unsupported format. Please upload MP3, WAV, M4A, OGG, or WebM.");
      return;
    }

    setVoiceFile(file);
  }

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    setError("");

    if (file.size > 50 * 1024 * 1024) {
      setError("Video exceeds the 50 MB limit.");
      return;
    }

    const validTypes = ["video/mp4", "video/quicktime", "video/webm"];
    if (!validTypes.includes(file.type)) {
      setError("Unsupported format. Please upload MP4, MOV, or WebM.");
      return;
    }

    setVideoFile(file);
    setVideoPreviewUrl(URL.createObjectURL(file));
  }

  async function handleUpload() {
    if (!voiceFile || !videoFile) return;

    setError("");
    setUploading(true);

    try {
      // Upload voice sample
      const voiceFormData = new FormData();
      voiceFormData.append("file", voiceFile);
      const voiceData = await apiFetch("/upload/voice", {
        method: "POST",
        body: voiceFormData,
      });
      setVoiceUrl(voiceData.url);

      // Upload video
      const videoFormData = new FormData();
      videoFormData.append("file", videoFile);
      const videoData = await apiFetch("/upload/video", {
        method: "POST",
        body: videoFormData,
      });
      setVideoUrl(videoData.url);

      setStep(1);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  // ── Step 2: Set pause point ───────────────────────────────

  function handlePauseConfirm() {
    setError("");

    const seconds = parseFloat(pauseSeconds);
    if (isNaN(seconds) || seconds < 0) {
      setError("Please enter a valid number of seconds.");
      return;
    }

    setStep(2);
  }

  // ── Step 3: Add names ─────────────────────────────────────

  function handleNamesConfirm() {
    setError("");

    const lines = namesText
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (lines.length === 0) {
      setError("Please enter at least one name.");
      return;
    }

    if (lines.length > 500) {
      setError("Maximum 500 names per batch.");
      return;
    }

    const seen = new Set();
    const cleaned = [];
    for (const name of lines) {
      const capitalized = name.charAt(0).toUpperCase() + name.slice(1);
      const key = capitalized.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        cleaned.push(capitalized);
      }
    }

    setCleanedNames(cleaned);
    setStep(3);
  }

  // ── Step 4: Review & create ───────────────────────────────

  async function handleCreate() {
    setError("");
    setCreating(true);

    try {
      const project = await apiFetch("/projects", {
        method: "POST",
        body: JSON.stringify({
          voice_sample_url: voiceUrl,
          source_video_url: videoUrl,
          pause_timestamp_ms: Math.round(parseFloat(pauseSeconds) * 1000),
          title: title || null,
        }),
      });

      await apiFetch(`/projects/${project.id}/names`, {
        method: "POST",
        body: JSON.stringify({ names: cleanedNames }),
      });

      await apiFetch(`/projects/${project.id}/generate`, {
        method: "POST",
      });

      navigate(`/projects/${project.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="text-xl font-heading font-bold">
            Namedropper
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8">
          {STEPS.map((label, index) => (
            <div key={label} className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index <= step
                    ? "bg-brand-red text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {index + 1}
              </div>
              <span
                className={`text-sm hidden sm:inline ${
                  index <= step ? "text-gray-900" : "text-gray-400"
                }`}
              >
                {label}
              </span>
              {index < STEPS.length - 1 && (
                <div className="w-8 h-px bg-gray-300" />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-8">
          {/* ── Step 1: Upload files ── */}
          {step === 0 && (
            <div>
              <h2 className="text-xl font-heading font-semibold mb-2">
                Upload your files
              </h2>
              <p className="text-gray-600 mb-6">
                Upload a voice sample (for cloning your voice) and your video
                (with a pause where names will be inserted).
              </p>

              {/* Voice sample */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voice sample (audio)
                </label>
                <p className="text-xs text-gray-400 mb-2">
                  Record at least 30 seconds of yourself speaking clearly.
                  MP3, WAV, M4A, OGG, or WebM. Max 10 MB.
                </p>
                {!voiceFile ? (
                  <label className="block border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-gray-400 transition-colors">
                    <input
                      type="file"
                      accept="audio/mpeg,audio/wav,audio/mp4,audio/x-m4a,audio/ogg,audio/webm,.mp3,.wav,.m4a,.ogg"
                      onChange={handleVoiceSelect}
                      className="hidden"
                    />
                    <div className="flex flex-col items-center gap-2">
                      <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
                      </svg>
                      <p className="text-gray-500">Click to select a voice sample</p>
                    </div>
                  </label>
                ) : (
                  <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-sm text-gray-600">
                        {voiceFile.name} ({(voiceFile.size / 1024 / 1024).toFixed(1)} MB)
                      </span>
                    </div>
                    <button
                      onClick={() => setVoiceFile(null)}
                      className="text-sm text-gray-500 hover:text-gray-700"
                    >
                      Change
                    </button>
                  </div>
                )}
              </div>

              {/* Video */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video
                </label>
                <p className="text-xs text-gray-400 mb-2">
                  Your video with a deliberate pause where names will be
                  inserted. MP4, MOV, or WebM. Max 60 seconds, max 50 MB.
                  Does not need to contain speech.
                </p>
                {!videoFile ? (
                  <label className="block border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-gray-400 transition-colors">
                    <input
                      type="file"
                      accept="video/mp4,video/quicktime,video/webm"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <div className="flex flex-col items-center gap-2">
                      <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
                      </svg>
                      <p className="text-gray-500">Click to select a video file</p>
                    </div>
                  </label>
                ) : (
                  <div>
                    {videoPreviewUrl && (
                      <video
                        src={videoPreviewUrl}
                        controls
                        className="w-full rounded-lg mb-3 max-h-64 bg-black"
                      />
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">
                        {videoFile.name} ({(videoFile.size / 1024 / 1024).toFixed(1)} MB)
                      </span>
                      <button
                        onClick={() => {
                          setVideoFile(null);
                          setVideoPreviewUrl("");
                        }}
                        className="text-sm text-gray-500 hover:text-gray-700"
                      >
                        Change
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={handleUpload}
                disabled={!voiceFile || !videoFile || uploading}
                className="w-full bg-brand-red text-white py-3 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {uploading ? "Uploading..." : "Upload and continue"}
              </button>
            </div>
          )}

          {/* ── Step 2: Pause timestamp ── */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-heading font-semibold mb-2">
                Where does the pause start?
              </h2>
              <p className="text-gray-600 mb-6">
                Play your video and note the second where the pause for
                the name begins.
              </p>

              {videoPreviewUrl && (
                <video
                  src={videoPreviewUrl}
                  controls
                  className="w-full rounded-lg mb-6 max-h-64 bg-black"
                />
              )}

              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pause starts at (seconds)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={pauseSeconds}
                onChange={(event) => setPauseSeconds(event.target.value)}
                placeholder="e.g. 3.5"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent outline-none"
              />

              <label className="block text-sm font-medium text-gray-700 mb-1 mt-4">
                Project title (optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="e.g. Training welcome video"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent outline-none"
              />

              <button
                onClick={handlePauseConfirm}
                className="mt-4 w-full bg-brand-red text-white py-3 rounded-lg font-medium hover:bg-red-700 transition-colors"
              >
                Continue
              </button>
            </div>
          )}

          {/* ── Step 3: Add names ── */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-heading font-semibold mb-2">
                Add names
              </h2>
              <p className="text-gray-600 mb-6">
                Enter the first names of your recipients, one per line.
              </p>

              <textarea
                rows={10}
                value={namesText}
                onChange={(event) => setNamesText(event.target.value)}
                placeholder={"Maria\nThomas\nSophie\nJames"}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-red focus:border-transparent outline-none font-mono text-sm"
              />

              <p className="text-xs text-gray-400 mt-2">
                Max 500 names per batch. Duplicates will be removed
                automatically.
              </p>

              <button
                onClick={handleNamesConfirm}
                className="mt-4 w-full bg-brand-red text-white py-3 rounded-lg font-medium hover:bg-red-700 transition-colors"
              >
                Review
              </button>
            </div>
          )}

          {/* ── Step 4: Review ── */}
          {step === 3 && (
            <div>
              <h2 className="text-xl font-heading font-semibold mb-6">
                Review and generate
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Project</span>
                  <span className="font-medium">
                    {title || "Untitled project"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Voice sample</span>
                  <span className="font-medium text-emerald-600">Uploaded</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Pause at</span>
                  <span className="font-medium">{pauseSeconds} seconds</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Names</span>
                  <span className="font-medium">
                    {cleanedNames.length} names
                  </span>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6 max-h-48 overflow-y-auto">
                <p className="text-xs text-gray-500 mb-2">Name list:</p>
                <div className="flex flex-wrap gap-2">
                  {cleanedNames.map((name) => (
                    <span
                      key={name}
                      className="bg-white border border-gray-200 text-sm px-2.5 py-1 rounded-full"
                    >
                      {name}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={handleCreate}
                disabled={creating}
                className="w-full bg-brand-red text-white py-3 rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {creating
                  ? "Creating..."
                  : `Generate ${cleanedNames.length} videos`}
              </button>
            </div>
          )}

          {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

          {/* Back button */}
          {step > 0 && (
            <button
              onClick={() => setStep(step - 1)}
              className="mt-4 text-sm text-gray-500 hover:text-gray-700"
            >
              Back
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
