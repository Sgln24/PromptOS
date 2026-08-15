import { create } from 'zustand';
import { ExtractedIntent, TaskSpecification, RecommendationResult } from './types';

interface PromptOSState {
  step: 'INPUT' | 'CLARIFYING' | 'COMPILING' | 'BENCHMARKING' | 'DONE';
  originalPrompt: string;
  targetProvider: string;
  generationMode: 'interactive' | 'direct';
  intent: ExtractedIntent | null;
  specification: TaskSpecification | null;
  recommendation: RecommendationResult | null;
  compiledResult: string | null;
  resolvedClarifications: Record<string, string>; // <-- Added to remember answers

  setOriginalPrompt: (text: string) => void;
  setTargetProvider: (provider: string) => void;
  setGenerationMode: (mode: 'interactive' | 'direct') => void;
  processPrompt: () => Promise<void>;
  submitClarifications: (answers: Record<string, string>) => Promise<void>;
  changeProviderAndRecompile: (provider: string) => Promise<void>; // <-- New feature
  refinePrompt: (extraDetails: string) => Promise<void>; // <-- New feature
}

export const usePromptOS = create<PromptOSState>()((set, get) => ({
  step: 'INPUT',
  originalPrompt: '',
  targetProvider: 'anthropic',
  generationMode: 'interactive',
  intent: null,
  specification: null,
  recommendation: null,
  compiledResult: null,
  resolvedClarifications: {},

  setOriginalPrompt: (text) => set({ originalPrompt: text }),
  setTargetProvider: (provider) => set({ targetProvider: provider }),
  setGenerationMode: (mode) => set({ generationMode: mode }),

  processPrompt: async () => {
    const { originalPrompt, targetProvider, generationMode } = get(); 

    set({ step: 'COMPILING' });

    try {
      const response = await fetch('http://localhost:8002/api/v1/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_prompt: originalPrompt,
          target_provider: targetProvider,
          skip_clarification: generationMode === 'direct'
        })
      });

      const data = await response.json();

      if (data.error) {
        alert(`Compilation Error: ${data.error}`);
        set({ step: 'INPUT' });
        return;
      }

      if (data.requires_clarification) {
        set({ step: 'CLARIFYING', intent: data.intent });
        return;
      }

      set({
        step: 'DONE',
        specification: data.specification,
        recommendation: data.recommendation,
        compiledResult: data.compiled_prompt || "No prompt returned from server."
      });

    } catch (error) {
      console.error("Compilation failed:", error);
      set({ step: 'INPUT' });
    }
  },

  submitClarifications: async (answers: Record<string, string>) => {
    const { originalPrompt, targetProvider } = get(); 

    set({ step: 'COMPILING', resolvedClarifications: answers }); // Save answers

    try {
      const response = await fetch('http://localhost:8002/api/v1/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_prompt: originalPrompt,
          target_provider: targetProvider,
          resolved_clarifications: answers 
        })
      });

      const data = await response.json();

      if (data.error) {
        alert(`Compilation Error: ${data.error}`);
        set({ step: 'INPUT' });
        return;
      }

      set({
        step: 'DONE',
        specification: data.specification,
        recommendation: data.recommendation,
        compiledResult: data.compiled_prompt || "No prompt returned from server."
      });

    } catch (error) {
      console.error("Failed to submit clarifications:", error);
      set({ step: 'INPUT' });
    }
  },

  // --- NEW: Instant Model Swapping ---
  changeProviderAndRecompile: async (newProvider: string) => {
    set({ targetProvider: newProvider, step: 'COMPILING' });
    const { originalPrompt, resolvedClarifications } = get();

    try {
      const response = await fetch('http://localhost:8002/api/v1/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_prompt: originalPrompt,
          target_provider: newProvider,
          skip_clarification: true, // Bypass Phase 1, we already have the intent!
          resolved_clarifications: resolvedClarifications
        })
      });

      const data = await response.json();
      
      if (data.error) {
        alert(`Compilation Error: ${data.error}`);
        set({ step: 'DONE' });
        return;
      }

      set({ step: 'DONE', compiledResult: data.compiled_prompt });
    } catch (error) {
      console.error("Failed to swap provider:", error);
      set({ step: 'DONE' });
    }
  },

  // --- NEW: Iterative Refinement Loop ---
  refinePrompt: async (extraDetails: string) => {
    const { originalPrompt } = get();
    // Append the new details to the original prompt
    const combinedPrompt = `${originalPrompt}\n\nAdditional Client Details:\n${extraDetails}`;
    
    set({
      originalPrompt: combinedPrompt,
      resolvedClarifications: {}, // Clear old answers so Qwen can ask new questions
      step: 'COMPILING'
    });

    // Re-trigger the whole process from the top
    get().processPrompt();
  }
}));