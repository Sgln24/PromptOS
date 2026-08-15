import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TaskSpecification } from '@/lib/types';

export default function PromptDiffViewer({ original, compiled, spec }: { original: string, compiled: string, spec: TaskSpecification }) {
  return (
    <div className="grid grid-cols-2 gap-6 h-full">
      {/* Original Request Pane */}
      <Card className="p-4 bg-slate-50 flex flex-col">
        <h4 className="text-sm font-semibold text-slate-500 mb-2 border-b pb-2">ORIGINAL REQUEST</h4>
        <p className="text-slate-800 whitespace-pre-wrap flex-1">
          {original}
        </p>
      </Card>

      {/* Compiled Prompt Pane */}
      <Card className="p-4 bg-slate-900 text-slate-100 flex flex-col font-mono text-sm shadow-xl">
        <div className="flex justify-between items-center mb-4 border-b border-slate-700 pb-2">
          <h4 className="text-sm font-semibold text-slate-400">COMPILED PROMPT (XML Dialect)</h4>
          <Badge variant="secondary">{spec.strategy_applied}</Badge>
        </div>
        
        <div className="overflow-y-auto space-y-4">
          {/* Role Diff */}
          {spec.role_persona && (
            <div className="group relative">
              <span className="text-green-400">{"<role>"}</span>
              <p className="pl-4 text-green-200">{spec.role_persona}</p>
              <span className="text-green-400">{"</role>"}</span>
              <div className="absolute right-0 top-0 hidden group-hover:block bg-slate-800 text-xs p-2 rounded">
                Added by Linter (RoleAssignmentRule)
              </div>
            </div>
          )}

          {/* Constraints Diff */}
          {spec.constraints.length > 0 && (
            <div className="group relative border-l-2 border-blue-500 pl-2">
              <span className="text-blue-400">{"<constraints>"}</span>
              <ul className="pl-4 text-blue-200 list-disc list-inside">
                {spec.constraints.map((c: any, i: any) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
              <span className="text-blue-400">{"</constraints>"}</span>
              <div className="absolute right-0 top-0 hidden group-hover:block bg-slate-800 text-xs p-2 rounded">
                Injected via Knowledge Engine RAG
              </div>
            </div>
          )}

          {/* Original Task */}
          <div>
            <span className="text-slate-400">{"<task>"}</span>
            <p className="pl-4 text-slate-100">{spec.primary_objective}</p>
            <span className="text-slate-400">{"</task>"}</span>
          </div>
        </div>
      </Card>
    </div>
  );
}