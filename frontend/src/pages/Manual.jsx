import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

function StepCard({ number, title, children }) {
  return (
    <div className="flex gap-5">
      <div className="flex-shrink-0">
        <div className="w-10 h-10 bg-brand-red rounded-xl flex items-center justify-center shadow-sm">
          <span className="text-white font-heading font-bold">{number}</span>
        </div>
      </div>
      <div className="flex-1 pb-8 border-b border-gray-100 last:border-0">
        <h3 className="font-heading font-semibold text-lg mb-2">{title}</h3>
        <div className="text-gray-500 space-y-2">{children}</div>
      </div>
    </div>
  );
}

function TipBox({ children }) {
  return (
    <div className="flex gap-3 bg-brand-warm rounded-xl p-4 text-sm text-gray-600 mt-3">
      <svg className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
      </svg>
      <span>{children}</span>
    </div>
  );
}

function TroubleshootItem({ title, children }) {
  return (
    <div className="flex gap-4 py-4 border-b border-gray-100 last:border-0">
      <div className="flex-shrink-0 mt-1">
        <div className="w-6 h-6 bg-red-50 rounded-full flex items-center justify-center">
          <svg className="w-3.5 h-3.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        </div>
      </div>
      <div>
        <p className="font-medium text-gray-900 mb-1">{title}</p>
        <p className="text-gray-500 text-sm">{children}</p>
      </div>
    </div>
  );
}

export default function Manual() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            to={token ? "/dashboard" : "/"}
            className="flex items-center gap-3"
          >
            <div className="w-8 h-8 bg-brand-red rounded-lg flex items-center justify-center">
              <span className="text-white font-heading font-bold text-sm">N</span>
            </div>
            <span className="font-heading font-bold tracking-tight">Namedropper</span>
          </Link>
          {token && (
            <Link to="/dashboard" className="text-sm text-gray-400 hover:text-gray-600 transition-colors">
              Back to dashboard
            </Link>
          )}
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10">
        {/* Hero */}
        <div className="card p-10 mb-8 bg-gradient-to-br from-white to-brand-warm/30">
          <h1 className="text-3xl font-heading font-bold text-gray-900 mb-3 tracking-tight">
            Hi Lavinia
          </h1>
          <p className="text-gray-500 text-lg leading-relaxed max-w-xl">
            Welcome to Namedropper. This manual walks you through every step,
            from recording your video to downloading the personalized
            versions. It is simpler than it looks — you will have it down
            after the first time.
          </p>
        </div>

        {/* What Namedropper does */}
        <div className="card p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-brand-peach rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </div>
            <h2 className="text-xl font-heading font-bold">What Namedropper does</h2>
          </div>
          <p className="text-gray-500 mb-4 leading-relaxed">
            You record a short video where you leave a pause for the
            recipient's name. Namedropper clones your voice, speaks each
            name in that voice, and inserts it into the pause. The result:
            every person gets a video where you personally say their name.
          </p>
          <div className="bg-gray-50 rounded-xl p-5 text-sm">
            <p className="text-gray-600">
              <span className="font-semibold text-gray-900">Example: </span>
              You record{" "}
              <em className="text-brand-red">
                "Hi ... [2-second pause] ... thanks for taking 5 minutes to
                share your perspective."
              </em>{" "}
              Namedropper turns that into "Hi Maria, thanks for...", "Hi Thomas, thanks for...", and so
              on — for every name on your list.
            </p>
          </div>
        </div>

        {/* What you need */}
        <div className="card p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-brand-peach rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-heading font-bold">What you need before you start</h2>
          </div>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="w-7 h-7 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-heading font-bold text-gray-500">1</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">A recorded video</p>
                <p className="text-sm text-gray-500 mt-0.5">MP4, MOV, or WebM. Max 60 seconds, max 50 MB. Record on your phone, laptop, or any camera. Must have audio.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-7 h-7 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-heading font-bold text-gray-500">2</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">A clear pause in the video</p>
                <p className="text-sm text-gray-500 mt-0.5">Stop talking for about 2 seconds where you want the name inserted. Just pause naturally.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-7 h-7 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs font-heading font-bold text-gray-500">3</span>
              </div>
              <div>
                <p className="font-medium text-gray-900">A list of first names</p>
                <p className="text-sm text-gray-500 mt-0.5">Up to 500 names per batch.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Step by step */}
        <div className="card p-8 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 bg-brand-peach rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
              </svg>
            </div>
            <h2 className="text-xl font-heading font-bold">Step by step</h2>
          </div>

          <div className="space-y-6">
            <StepCard number="1" title="Log in">
              <p>
                Go to the Namedropper website. Enter your email address and
                click <strong className="text-gray-900">"Log in"</strong>. You are in — no password needed.
              </p>
            </StepCard>

            <StepCard number="2" title="Create a new project">
              <p>
                On the dashboard, click <strong className="text-gray-900">"New project"</strong>. You
                will see a step-by-step wizard. Just follow it — each step explains
                what to do.
              </p>
            </StepCard>

            <StepCard number="3" title="Upload your video">
              <p>
                Click the upload area and select your video file. The tool
                checks that the file is valid (right format, not too large).
                After uploading, you can play it back to double-check.
              </p>
              <TipBox>
                Record in a quiet room. The voice cloning works best with clean audio. Background noise will not break it, but the cleaner the recording, the more natural the result.
              </TipBox>
            </StepCard>

            <StepCard number="4" title="Set the pause point">
              <p>
                Play your video and note the exact second where the pause
                starts. Enter that number. For example, if you say "Hi" and
                then pause at the 2-second mark, type <strong className="text-gray-900">2</strong> (or
                2.5 if it is between seconds).
              </p>
              <p>
                You can also give the project a name here (optional but helpful if you create multiple projects).
              </p>
              <TipBox>
                You can play the video right there on the page while you figure out the timestamp. Take your time to get it right — it determines where the name gets inserted.
              </TipBox>
            </StepCard>

            <StepCard number="5" title="Add names">
              <p>
                Type or paste your list of first names, one per line. The tool automatically:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-1 text-gray-500">
                <li>Capitalizes the first letter of each name</li>
                <li>Removes duplicates</li>
                <li>Strips extra spaces</li>
              </ul>
              <p>You will see the cleaned list before confirming.</p>
            </StepCard>

            <StepCard number="6" title="Review and generate">
              <p>
                You see a summary: the project name, the pause timestamp, and
                the full name list. If everything looks right, click{" "}
                <strong className="text-gray-900">"Generate X videos"</strong>. Namedropper starts working.
              </p>
            </StepCard>

            <StepCard number="7" title="Wait for processing">
              <p>
                You are taken to the project page, which shows a live progress
                bar. Each name goes through these stages:
              </p>
              <div className="space-y-2 mt-2">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-gray-300" />
                  <span><strong className="text-gray-700">Pending</strong> — in the queue</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                  <span><strong className="text-gray-700">Generating audio</strong> — the voice clone is speaking the name</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                  <span><strong className="text-gray-700">Splicing</strong> — inserting the name into the video</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span><strong className="text-gray-700">Completed</strong> — ready to preview and download</span>
                </div>
              </div>
              <p className="mt-3">
                Processing takes about 3-5 seconds per name. So 50 names takes
                roughly 3-4 minutes. You can leave the page open and it
                updates automatically — no need to refresh.
              </p>
              <TipBox>
                You will also receive an email when the entire batch is finished, so you do not have to sit and watch.
              </TipBox>
            </StepCard>

            <StepCard number="8" title="Preview and download">
              <p>Once a name is completed, you can:</p>
              <ul className="list-disc list-inside space-y-1 ml-1 text-gray-500">
                <li><strong className="text-gray-700">Play it</strong> in the browser — click the video player on the card</li>
                <li><strong className="text-gray-700">Download one video</strong> — click "Download" under the player</li>
                <li><strong className="text-gray-700">Download all</strong> — click the "Download all" button for a ZIP file with every completed video</li>
              </ul>
              <p className="mt-2">
                Each file is named after the person:{" "}
                <code className="bg-gray-100 px-2 py-0.5 rounded-md text-sm text-brand-red">Maria.mp4</code>,{" "}
                <code className="bg-gray-100 px-2 py-0.5 rounded-md text-sm text-brand-red">Thomas.mp4</code>, etc.
              </p>
            </StepCard>
          </div>
        </div>

        {/* Troubleshooting */}
        <div className="card p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-brand-peach rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17l-5.384 3.073A.75.75 0 015 17.622V6.378a.75.75 0 011.036-.62l5.384 3.073m0 6.339l5.384 3.073A.75.75 0 0017.964 17.622V6.378a.75.75 0 00-1.036-.62l-5.384 3.073" />
              </svg>
            </div>
            <h2 className="text-xl font-heading font-bold">If something goes wrong</h2>
          </div>

          <TroubleshootItem title={'"Video file exceeds the 50 MB limit"'}>
            Your video is too large. Try compressing it (most phones save in high resolution by default) or making it shorter. 60 seconds in 1080p is usually well under 50 MB.
          </TroubleshootItem>
          <TroubleshootItem title={'"Video must be at least 10 seconds"'}>
            The voice cloning needs enough audio to learn your voice. Record at least 10 seconds — ideally 20-30 seconds — for the best results.
          </TroubleshootItem>
          <TroubleshootItem title={'A name shows "Failed" with a red badge'}>
            This usually means the voice generation service had a temporary issue. You can delete the project and create a new one with the same video and names. If it keeps happening, reach out to Peter.
          </TroubleshootItem>
          <TroubleshootItem title={"The login link in my email does not work"}>
            Login links expire after 15 minutes and can only be used once. If yours expired, just go back to the login page and request a new one.
          </TroubleshootItem>
        </div>

        {/* Tips */}
        <div className="card p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-brand-peach rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-brand-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
              </svg>
            </div>
            <h2 className="text-xl font-heading font-bold">Tips for the best result</h2>
          </div>
          <div className="space-y-4 text-gray-500">
            <div className="flex gap-3">
              <span className="text-brand-red mt-1">*</span>
              <span><strong className="text-gray-900">Keep the pause clean.</strong> Do not trail off or make a sound during the pause. A clean silence gives the best splice.</span>
            </div>
            <div className="flex gap-3">
              <span className="text-brand-red mt-1">*</span>
              <span><strong className="text-gray-900">Speak naturally before and after the pause.</strong> The cloned voice matches your tone, so if you sound warm and relaxed, the name will too.</span>
            </div>
            <div className="flex gap-3">
              <span className="text-brand-red mt-1">*</span>
              <span><strong className="text-gray-900">Test with 2-3 names first.</strong> Before generating 200 videos, try a small batch to make sure the pause point is right and the result sounds natural.</span>
            </div>
            <div className="flex gap-3">
              <span className="text-brand-red mt-1">*</span>
              <span><strong className="text-gray-900">International names work.</strong> The voice engine supports 29 languages. Names like Xiaoming, Priya, or Bjorn will be pronounced correctly.</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center py-6 text-sm text-gray-400">
          <p>Questions? Message Peter.</p>
        </div>
      </main>
    </div>
  );
}
