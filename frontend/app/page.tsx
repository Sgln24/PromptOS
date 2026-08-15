"use client";

import { useState } from "react";
import { usePromptOS } from "@/lib/store";

export default function PromptOS() {
  const {
    step,
    originalPrompt,
    setOriginalPrompt,
    targetProvider,
    setTargetProvider,
    generationMode,
    setGenerationMode,
    processPrompt,
    submitClarifications,
    changeProviderAndRecompile, // <-- New action
    refinePrompt,               // <-- New action
    compiledResult,
    intent
  } = usePromptOS();

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [refinementText, setRefinementText] = useState(""); // <-- Local state for appending details

  const handleAnswerChange = (id: string, value: string) => {
    setAnswers(prev => ({ ...prev, [id]: value }));
  };

  // Helper component to keep the dropdown DRY (Don't Repeat Yourself)
  const ProviderOptions = () => (
    <>
      <option value="anthropic">Claude (Anthropic)</option>
      <option value="openai_gpt4">GPT-4 / Omni (OpenAI)</option>
      <option value="openai">o3-mini (OpenAI)</option>
      <option value="meta">Llama (Meta)</option>
      <option value="deepseek">DeepSeek Reasoner</option>
      <option value="google_gemini">Gemini (Google)</option>
      <option value="google">Gemma (Google IT)</option>
      <option value="mistral">Mistral AI</option>
      <option value="perplexity">Sonar (Perplexity)</option>
      <option value="xai">Grok-1 (xAI)</option>
      <option value="moonshot">Kimi K2.5 (Moonshot)</option>
      <option value="microsoft_copilot">Microsoft Copilot (M365)</option>
      <optgroup label="Coding Agents">
        <option value="cursor">Cursor AI Agent</option>
        <option value="github_copilot">GitHub Copilot</option>
        <option value="openai_codex">OpenAI Codex</option>
        <option value="blackbox">Blackbox AI</option>
      </optgroup>
      <optgroup label="Local Models">
        <option value="qwen_local">Local Qwen (Ollama)</option>
      </optgroup>
    </>
  );

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-10">
        <header className="mb-12 text-center">
          <div className="mb-4 inline-flex items-center rounded-full border border-zinc-800 bg-zinc-900 px-4 py-1 text-sm text-zinc-400">
            Prompt Engineering Operating System
          </div>
          <h1 className="mb-4 text-5xl font-bold tracking-tight">
            Prompt<span className="text-blue-500">OS</span>
          </h1>
          <p className="mx-auto max-w-3xl text-lg text-zinc-400">
            Transform simple ideas into production-grade prompts.
          </p>
        </header>

        <div className="grid flex-1 gap-8 lg:grid-cols-3">
          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 lg:col-span-2">
            
            {/* 1. INPUT STEP */}
            {step === 'INPUT' && (
              <>
                <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">Describe Your Goal</h2>
                  </div>
                  <div className="w-full sm:w-64">
                    <label className="block text-xs font-mono uppercase text-zinc-400 mb-1">Target Model</label>
                    <select
                      value={targetProvider}
                      onChange={(e) => setTargetProvider(e.target.value)}
                      className="w-full rounded-xl border border-zinc-700 bg-zinc-950 p-3 text-sm text-white outline-none"
                    >
                      <ProviderOptions />
                    </select>
                  </div>
                </div>

                <div className="mb-6 rounded-xl border border-zinc-800 bg-zinc-950/80 p-4">
                  <label className="block text-xs font-mono uppercase text-zinc-400 mb-2">Workflow Strategy</label>
                  <div className="flex flex-wrap items-center gap-4">
                    <button
                      onClick={() => setGenerationMode('interactive')}
                      className={`rounded-xl px-4 py-2 text-sm font-medium border transition ${
                        generationMode === 'interactive' ? 'border-blue-500 bg-blue-600/20 text-blue-400' : 'border-zinc-800 bg-zinc-900 text-zinc-400'
                      }`}
                    >
                      ✨ Interactive AI Consultation
                    </button>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setGenerationMode('direct')}
                        className={`rounded-xl px-4 py-2 text-sm font-medium border transition ${
                          generationMode === 'direct' ? 'border-blue-500 bg-blue-600/20 text-blue-400' : 'border-zinc-800 bg-zinc-900 text-zinc-400'
                        }`}
                      >
                        ⚡ Generate Directly <span className="text-xs text-zinc-500 italic">(not best practice)</span>
                      </button>
                      
                    </div>
                  </div>
                </div>

                <textarea
                  value={originalPrompt}
                  onChange={(e) => setOriginalPrompt(e.target.value)}
                  placeholder="Example: Build a SaaS platform..."
                  className="min-h-[260px] w-full rounded-xl border border-zinc-700 bg-zinc-950 p-5 text-base outline-none focus:border-blue-500"
                />

                <div className="mt-6 flex justify-end">
                  <button
                    onClick={processPrompt}
                    disabled={!originalPrompt}
                    className="rounded-xl bg-blue-600 px-8 py-3 font-semibold transition hover:bg-blue-500 disabled:opacity-50"
                  >
                    {generationMode === 'interactive' ? 'Analyze Requirements' : 'Generate Prompt'}
                  </button>
                </div>
              </>
            )}

            {/* 2. CLARIFYING STEP */}
            {step === 'CLARIFYING' && intent && (
              <div className="space-y-6">
                <div className="mb-6 border-b border-zinc-800 pb-4">
                  <h2 className="text-xl font-semibold text-blue-400">Expert Consultation</h2>
                  <p className="mt-2 text-sm text-zinc-400">
                    Acting as a <span className="font-bold text-zinc-200">{intent.role_assumed}</span>, our system needs a few more details.
                  </p>
                </div>
                
                {intent.questions.map((q) => (
                  <div key={q.id} className="space-y-2">
                    <label className="block text-sm font-medium text-zinc-300">{q.question}</label>
                    <input
                      type="text"
                      value={answers[q.id] || ''}
                      onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                      className="w-full rounded-lg border border-zinc-700 bg-zinc-950 p-3 text-sm outline-none focus:border-blue-500"
                    />
                  </div>
                ))}

                <div className="mt-8 flex justify-end gap-4">
                  <button
                    onClick={() => submitClarifications(answers)}
                    className="rounded-xl bg-blue-600 px-8 py-3 font-semibold transition hover:bg-blue-500"
                  >
                    Finalize & Compile
                  </button>
                </div>
              </div>
            )}

            {/* 3. COMPILING STEP */}
            {step === 'COMPILING' && (
              <div className="flex h-64 items-center justify-center">
                <div className="text-lg animate-pulse text-zinc-400">Compiling your optimized prompt...</div>
              </div>
            )}

            {/* 4. DONE STEP */}
            {step === 'DONE' && (
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-blue-400">Optimized Output</h2>
                  {compiledResult && (
                    <button 
                      onClick={() => navigator.clipboard.writeText(compiledResult)}
                      className="text-xs border border-zinc-700 hover:bg-zinc-800 rounded px-3 py-1 transition"
                    >
                      Copy to Clipboard
                    </button>
                  )}
                </div>

                {compiledResult ? (
                  <pre className="whitespace-pre-wrap text-sm text-zinc-300 font-mono bg-zinc-950 p-6 rounded-xl border border-zinc-800 overflow-x-auto">
                    {compiledResult}
                  </pre>
                ) : (
                  <div className="p-6 rounded-xl border border-red-800/50 bg-red-950/20 text-red-400 text-sm">
                    No optimized prompt returned. Please check the backend.
                  </div>
                )}

                {/* --- NEW: POST-GENERATION ACTIONS --- */}
                <div className="mt-8 grid gap-6 border-t border-zinc-800 pt-8 md:grid-cols-2">
                  
                  {/* Feature 2: Swap Provider */}
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
                    <h3 className="mb-1 text-base font-semibold text-zinc-200">Reformat Target</h3>
                    <p className="mb-4 text-xs text-zinc-500">Instantly recompile the prompt using a different company's formatting rules.</p>
                    <select
                      value={targetProvider}
                      onChange={(e) => changeProviderAndRecompile(e.target.value)}
                      className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-2.5 text-sm text-white outline-none focus:border-blue-500"
                    >
                      <ProviderOptions />
                    </select>
                  </div>

                  {/* Feature 1: Refine Prompt */}
                  <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-5">
                    <h3 className="mb-1 text-base font-semibold text-zinc-200">Iterate & Refine</h3>
                    <p className="mb-4 text-xs text-zinc-500">Add missing details. Qwen may ask new clarifying questions based on this.</p>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={refinementText}
                        onChange={(e) => setRefinementText(e.target.value)}
                        placeholder="e.g. Add dark mode to the UI..."
                        className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 p-2.5 text-sm outline-none focus:border-blue-500"
                      />
                      <button
                        onClick={() => {
                          if (refinementText.trim()) refinePrompt(refinementText);
                        }}
                        disabled={!refinementText.trim()}
                        className="rounded-lg bg-blue-600 px-4 text-sm font-semibold hover:bg-blue-500 disabled:opacity-50"
                      >
                        Refine
                      </button>
                    </div>
                  </div>
                </div>

                <div className="mt-8 text-center">
                  <button
                    onClick={() => window.location.reload()}
                    className="text-xs text-zinc-500 hover:text-zinc-300 transition underline underline-offset-4"
                  >
                    Start completely over
                  </button>
                </div>
              </div>
            )}
          </section>

          {/* Right Sidebar Status (remains the same) */}
          <aside className="space-y-6">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6">
              <h3 className="mb-3 text-lg font-semibold">System Status</h3>
              <div className="rounded-lg bg-zinc-950 p-4">
                <span className="text-sm text-zinc-400">Current State</span>
                <div className="mt-2 text-xl font-bold text-blue-400">{step}</div>
              </div>
            </div>

            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6">
              <h3 className="mb-4 text-lg font-semibold">Pipeline</h3>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li className={step !== 'INPUT' ? 'text-blue-400' : ''}>✓ Intent Detection (Qwen)</li>
                <li className={step === 'CLARIFYING' || step === 'COMPILING' || step === 'DONE' ? 'text-blue-400' : ''}>✓ Interactive Consultation</li>
                <li className={step === 'COMPILING' || step === 'DONE' ? 'text-blue-400' : ''}>✓ RAG Enterprise Guidelines</li>
                <li className={step === 'COMPILING' || step === 'DONE' ? 'text-blue-400' : ''}>✓ Intelligent Prompt Synthesis</li>
                <li className={step === 'DONE' ? 'text-blue-400' : ''}>✓ Provider Formatting Engine</li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}