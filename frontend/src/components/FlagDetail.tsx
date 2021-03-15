import React, { useState } from "react";

import { deleteRule, saveRule } from "../api/client";
import { Flag, OPERATOR_LABELS, TargetingRule } from "../types";
import RuleEditor from "./RuleEditor";

export default function FlagDetail({ flag }: { flag: Flag }) {
  const [rules, setRules] = useState<TargetingRule[]>(flag.rules);
  const [editing, setEditing] = useState<TargetingRule | null>(null);
  const [adding, setAdding] = useState(false);

  async function persist(rule: Partial<TargetingRule>) {
    const saved = await saveRule(flag.id, rule);
    setRules((prev) => {
      const rest = prev.filter((r) => r.id !== saved.id);
      return [...rest, saved].sort((a, b) => a.priority - b.priority);
    });
    setEditing(null);
    setAdding(false);
  }

  async function remove(rule: TargetingRule) {
    await deleteRule(flag.id, rule.id);
    setRules((prev) => prev.filter((r) => r.id !== rule.id));
  }

  return (
    <div className="flag-detail">
      <h2>{flag.key}</h2>
      <p className="flag-detail__description">{flag.description}</p>

      <h3>Targeting</h3>
      <ol className="flag-detail__rules">
        {rules.map((rule) => (
          <li key={rule.id}>
            {editing?.id === rule.id ? (
              <RuleEditor
                rule={rule}
                onSave={persist}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <span>
                <code>{rule.attribute}</code> {OPERATOR_LABELS[rule.operator]}{" "}
                <code>{rule.values}</code> &rarr; <strong>{rule.variant}</strong>
                <button onClick={() => setEditing(rule)}>Edit</button>
                <button onClick={() => remove(rule)}>Remove</button>
              </span>
            )}
          </li>
        ))}
      </ol>

      {adding ? (
        <RuleEditor onSave={persist} onCancel={() => setAdding(false)} />
      ) : (
        <button onClick={() => setAdding(true)}>Add rule</button>
      )}

      <p className="flag-detail__rollout">
        Everyone who matches no rule falls through to a {flag.rollout_percentage}%
        rollout.
      </p>
    </div>
  );
}
