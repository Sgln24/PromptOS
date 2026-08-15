export type TaskCategory = 'programming' | 'data_science' | 'writing' | 'research' | 'cybersecurity';
export type PromptStrategy = 'direct' | 'chain_of_thought' | 'few_shot' | 'react' | 'tree_of_thoughts';

export interface TaskSpecification {
  category: TaskCategory;
  primary_objective: string;
  role_persona?: string;
  context_data: string[];
  constraints: string[];
  output_format?: Record<string, string>;
  examples: Array<{ input: string; output: string }>;
  strategy_applied?: PromptStrategy;
}


export interface ClarificationQuestion {
  id: string;
  question: string;
}

export interface ExtractedIntent {
  role_assumed: string;
  questions: ClarificationQuestion[];
}

export interface ModelDefinition {
  id: string;
  name: string;
  provider: string;
  profile: any;
}

export interface ModelScore {
  model: ModelDefinition;
  total_score: number;
  capability_match_ratio: number;
  context_fit: boolean;
  pricing_score: number;
  reasoning: string[];
}

export interface RecommendationResult {
  primary_recommendation: ModelScore;
  alternatives: ModelScore[];
  summary_justification: string;
}

export interface ClarificationBatch {
  requires_user_input: boolean;
  confidence_score: number;
  questions: ClarificationQuestion[];
}