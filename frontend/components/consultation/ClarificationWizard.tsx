import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ClarificationBatch } from '@/lib/types';

export default function ClarificationWizard({ batch, onResolve }: { batch: ClarificationBatch, onResolve: (answers: Record<string, string>) => void }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  if (!batch.requires_user_input) return null;

  return (
    <Card className="p-6 border-l-4 border-l-blue-500 bg-slate-50">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800">PromptOS needs a bit more context</h3>
        <p className="text-sm text-slate-500">Confidence Score: {batch.confidence_score * 100}%</p>
      </div>

      <div className="space-y-6">
        {batch.questions.map((q: any) => (
          <div key={q.id} className="space-y-2">
            <label className="font-medium text-slate-700">{q.question}</label>
            <p className="text-xs text-slate-400 italic mb-2">Why we ask: {q.rationale}</p>
            
            <div className="flex gap-2 flex-wrap">
              {q.suggested_options?.map((opt: any) => (
                <Button 
                  key={opt} 
                  variant={answers[q.id] === opt ? "default" : "outline"}
                  onClick={() => setAnswers({...answers, [q.id]: opt})}
                >
                  {opt}
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <Button 
        className="mt-6 w-full" 
        onClick={() => onResolve(answers)}
        disabled={Object.keys(answers).length !== batch.questions.length}
      >
        Resume Compilation
      </Button>
    </Card>
  );
}