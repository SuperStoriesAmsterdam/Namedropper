import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Manual() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            to={token ? "/dashboard" : "/"}
            className="text-xl font-heading font-bold"
          >
            Namedropper
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl border border-gray-200 p-8 space-y-8">
          {/* Greeting */}
          <div>
            <h1 className="text-3xl font-heading font-bold text-gray-900 mb-3">
              Hi Lavinia
            </h1>
            <p className="text-gray-600 text-lg">
              Welcome to Namedropper. This manual walks you through every step,
              from recording your video to downloading the personalized
              versions. It is simpler than it looks — you will have it down
              after the first time.
            </p>
          </div>

          <hr className="border-gray-200" />

          {/* What Namedropper does */}
          <div>
            <h2 className="text-xl font-heading font-semibold mb-3">
              What Namedropper does
            </h2>
            <p className="text-gray-600 mb-3">
              You record a short video where you leave a pause for the
              recipient's name. Namedropper clones your voice, speaks each
              name in that voice, and inserts it into the pause. The result:
              every person gets a video where you personally say their name.
            </p>
            <p className="text-gray-600">
              <strong>Example:</strong> You record{" "}
              <em>
                "Hi ... [2-second pause] ... thanks for taking 5 minutes to
                share your perspective."
              </em>{" "}
              Namedropper turns that into "Hi Maria, thanks for taking 5
              minutes...", "Hi Thomas, thanks for taking 5 minutes...", and so
              on — for every name on your list.
            </p>
          </div>

          <hr className="border-gray-200" />

          {/* What you need */}
          <div>
            <h2 className="text-xl font-heading font-semibold mb-3">
              What you need before you start
            </h2>
            <ul className="space-y-2 text-gray-600">
              <li className="flex gap-3">
                <span className="text-brand-red font-bold">1.</span>
                <span>
                  <strong>A recorded video</strong> (MP4, MOV, or WebM). Max 60
                  seconds, max 50 MB. Record it on your phone, laptop, or any
                  camera. Make sure it has audio — a silent video will not work.
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand-red font-bold">2.</span>
                <span>
                  <strong>A clear pause in the video</strong> where the name
                  should go. Just stop talking for about 2 seconds at the spot
                  where you want the name inserted. You do not need to do
                  anything special — just pause naturally.
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand-red font-bold">3.</span>
                <span>
                  <strong>A list of first names</strong>. You can have up to 500
                  names per batch.
                </span>
              </li>
            </ul>
          </div>

          <hr className="border-gray-200" />

          {/* Step by step */}
          <div>
            <h2 className="text-xl font-heading font-semibold mb-4">
              Step by step
            </h2>

            {/* Step 1 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  1
                </span>
                Log in
              </h3>
              <p className="text-gray-600 ml-9">
                Go to the Namedropper website. Enter your email address and
                click <strong>"Send login link"</strong>. Check your inbox —
                you will receive an email with a link. Click the link and you
                are logged in. No password needed, ever.
              </p>
            </div>

            {/* Step 2 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  2
                </span>
                Create a new project
              </h3>
              <p className="text-gray-600 ml-9">
                On the dashboard, click <strong>"New project"</strong>. You
                will see a 4-step wizard. Just follow it — each step explains
                what to do.
              </p>
            </div>

            {/* Step 3 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  3
                </span>
                Upload your video
              </h3>
              <p className="text-gray-600 ml-9 mb-2">
                Click the upload area and select your video file. The tool
                checks that the file is valid (right format, not too large).
                After uploading, you can play it back to double-check.
              </p>
              <div className="ml-9 bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
                <strong>Tip:</strong> Record in a quiet room. The voice
                cloning works best with clean audio. Background noise will not
                break it, but the cleaner the recording, the more natural the
                result.
              </div>
            </div>

            {/* Step 4 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  4
                </span>
                Set the pause point
              </h3>
              <p className="text-gray-600 ml-9 mb-2">
                Play your video and note the exact second where the pause
                starts. Enter that number. For example, if you say "Hi" and
                then pause at the 2-second mark, type <strong>2</strong> (or
                2.5 if it is between seconds).
              </p>
              <p className="text-gray-600 ml-9">
                You can also give the project a name here (optional but
                helpful if you create multiple projects).
              </p>
              <div className="ml-9 bg-gray-50 rounded-lg p-4 text-sm text-gray-500 mt-2">
                <strong>Tip:</strong> You can play the video right there on
                the page while you figure out the timestamp. Take your time to
                get it right — it determines where the name gets inserted.
              </div>
            </div>

            {/* Step 5 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  5
                </span>
                Add names
              </h3>
              <p className="text-gray-600 ml-9 mb-2">
                Type or paste your list of first names, one per line. The tool
                automatically:
              </p>
              <ul className="text-gray-600 ml-9 list-disc list-inside space-y-1">
                <li>Capitalizes the first letter of each name</li>
                <li>Removes duplicates</li>
                <li>Strips extra spaces</li>
              </ul>
              <p className="text-gray-600 ml-9 mt-2">
                You will see the cleaned list before confirming.
              </p>
            </div>

            {/* Step 6 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  6
                </span>
                Review and generate
              </h3>
              <p className="text-gray-600 ml-9">
                You see a summary: the project name, the pause timestamp, and
                the full name list. If everything looks right, click{" "}
                <strong>"Generate X videos"</strong>. Namedropper starts
                working.
              </p>
            </div>

            {/* Step 7 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  7
                </span>
                Wait for processing
              </h3>
              <p className="text-gray-600 ml-9 mb-2">
                You are taken to the project page, which shows a live progress
                bar. Each name goes through these stages:
              </p>
              <ul className="text-gray-600 ml-9 space-y-1">
                <li>
                  <span className="inline-block w-2 h-2 rounded-full bg-gray-400 mr-2" />
                  <strong>Pending</strong> — in the queue
                </li>
                <li>
                  <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 mr-2" />
                  <strong>Generating audio</strong> — the voice clone is
                  speaking the name
                </li>
                <li>
                  <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 mr-2" />
                  <strong>Splicing</strong> — inserting the name into the video
                </li>
                <li>
                  <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-2" />
                  <strong>Completed</strong> — ready to preview and download
                </li>
              </ul>
              <p className="text-gray-600 ml-9 mt-2">
                Processing takes about 3-5 seconds per name. So 50 names takes
                roughly 3-4 minutes. You can leave the page open and it
                updates automatically — no need to refresh.
              </p>
              <div className="ml-9 bg-gray-50 rounded-lg p-4 text-sm text-gray-500 mt-2">
                <strong>Note:</strong> You will also receive an email when the
                entire batch is finished, so you do not have to sit and watch.
              </div>
            </div>

            {/* Step 8 */}
            <div className="mb-6">
              <h3 className="font-heading font-semibold text-lg mb-2">
                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-brand-red text-white text-sm font-bold mr-2">
                  8
                </span>
                Preview and download
              </h3>
              <p className="text-gray-600 ml-9 mb-2">
                Once a name is completed, you can:
              </p>
              <ul className="text-gray-600 ml-9 list-disc list-inside space-y-1">
                <li>
                  <strong>Play it</strong> in the browser — click the video
                  player on the card
                </li>
                <li>
                  <strong>Download one video</strong> — click "Download" under
                  the player
                </li>
                <li>
                  <strong>Download all</strong> — click the "Download all"
                  button at the top right to get a ZIP file with every
                  completed video
                </li>
              </ul>
              <p className="text-gray-600 ml-9 mt-2">
                Each file is named after the person:{" "}
                <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">
                  Maria.mp4
                </code>
                ,{" "}
                <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm">
                  Thomas.mp4
                </code>
                , etc.
              </p>
            </div>
          </div>

          <hr className="border-gray-200" />

          {/* If something goes wrong */}
          <div>
            <h2 className="text-xl font-heading font-semibold mb-3">
              If something goes wrong
            </h2>
            <div className="space-y-4 text-gray-600">
              <div>
                <p className="font-medium text-gray-900">
                  "Video file exceeds the 50 MB limit"
                </p>
                <p>
                  Your video is too large. Try compressing it (most phones save
                  in high resolution by default) or making it shorter. 60
                  seconds in 1080p is usually well under 50 MB.
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  "Video must be at least 10 seconds"
                </p>
                <p>
                  The voice cloning needs enough audio to learn your voice.
                  Record at least 10 seconds — ideally 20-30 seconds — for
                  the best results.
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  A name shows "Failed" with a red badge
                </p>
                <p>
                  This usually means the voice generation service had a
                  temporary issue. You can delete the project and create a new
                  one with the same video and names. If it keeps happening,
                  reach out to Peter.
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  The login link in my email does not work
                </p>
                <p>
                  Login links expire after 15 minutes and can only be used
                  once. If yours expired, just go back to the login page and
                  request a new one.
                </p>
              </div>
            </div>
          </div>

          <hr className="border-gray-200" />

          {/* Tips */}
          <div>
            <h2 className="text-xl font-heading font-semibold mb-3">
              Tips for the best result
            </h2>
            <ul className="space-y-3 text-gray-600">
              <li className="flex gap-3">
                <span className="text-brand-red font-bold text-lg">*</span>
                <span>
                  <strong>Keep the pause clean.</strong> Do not trail off or
                  make a sound during the pause. A clean silence gives the
                  best splice.
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand-red font-bold text-lg">*</span>
                <span>
                  <strong>Speak naturally before and after the pause.</strong>{" "}
                  The cloned voice matches your tone, so if you sound warm and
                  relaxed, the name will too.
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand-red font-bold text-lg">*</span>
                <span>
                  <strong>Test with 2-3 names first.</strong> Before
                  generating 200 videos, try a small batch to make sure the
                  pause point is right and the result sounds natural.
                </span>
              </li>
              <li className="flex gap-3">
                <span className="text-brand-red font-bold text-lg">*</span>
                <span>
                  <strong>International names work.</strong> The voice engine
                  supports 29 languages. Names like Xiǎomíng, Priya, or
                  Björn will be pronounced correctly.
                </span>
              </li>
            </ul>
          </div>

          <hr className="border-gray-200" />

          <div className="text-center text-sm text-gray-400">
            <p>
              Questions? Message Peter. He built this.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
