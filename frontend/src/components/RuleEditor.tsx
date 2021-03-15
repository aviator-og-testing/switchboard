import React, { useState } from "react";

import { OPERATOR_LABELS, Operator, TargetingRule } from "../types";

interface Props {
  rule?: TargetingRule;
  onSave: (rule: Partial<TargetingRule>) => void;
  onCancel: () => void;
}

const OPERATORS = Object.keys(OPERATOR_LABELS) as Operator[];

export default function RuleEditor({ rule, onSave, onCancel }: Props) {
  const [attribute, setAttribute] = useState(rule?.attribute || "");
  const [operator, setOperator] = useState<Operator>(rule?.operator || "in");
  const [values, setValues] = useState(rule?.values || "");
  const [variant, setVariant] = useState(rule?.variant || "on");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    onSave({ id: rule?.id, attribute, operator, values, variant });
  }

  return (
    <form className="rule-editor" onSubmit={submit}>
      <input
        className="rule-editor__attribute"
        placeholder="attribute (plan, email, app_version)"
        value={attribute}
        onChange={(e) => setAttribute(e.target.value)}
      />

      <select
        className="rule-editor__operator"
        value={operator}
        onChange={(e) => setOperator(e.target.value as Operator)}
      >
        {OPERATORS.map((op) => (
          <option key={op} value={op}>
            {OPERATOR_LABELS[op]}
          </option>
        ))}
      </select>

      <input
        className="rule-editor__values"
        placeholder="comma separated"
        value={values}
        onChange={(e) => setValues(e.target.value)}
      />

      <input
        className="rule-editor__variant"
        placeholder="variant"
        value={variant}
        onChange={(e) => setVariant(e.target.value)}
      />

      <button type="submit">Save</button>
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
    </form>
  );
}
