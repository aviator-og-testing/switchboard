export type Operator = "in" | "not_in" | "contains" | "regex" | "semver_gt";

export interface TargetingRule {
  id: number;
  priority: number;
  attribute: string;
  operator: Operator;
  values: string;
  variant: string;
}

export interface Flag {
  id: number;
  key: string;
  description: string;
  enabled: boolean;
  default_variant: string;
  rollout_percentage: number;
  rules: TargetingRule[];
}

export const OPERATOR_LABELS: Record<Operator, string> = {
  in: "is one of",
  not_in: "is not one of",
  contains: "contains",
  regex: "matches regex",
  semver_gt: "version is newer than",
};
