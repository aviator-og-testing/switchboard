import React, { useEffect, useState } from "react";

import { listFlags, updateFlag } from "../api/client";
import { Flag } from "../types";

export default function FlagList({
  onSelect,
}: {
  onSelect: (flag: Flag) => void;
}) {
  const [flags, setFlags] = useState<Flag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listFlags()
      .then(setFlags)
      .finally(() => setLoading(false));
  }, []);

  async function toggle(flag: Flag) {
    const updated = await updateFlag(flag.id, { enabled: !flag.enabled });
    setFlags((prev) => prev.map((f) => (f.id === updated.id ? updated : f)));
  }

  if (loading) {
    return <div className="flag-list__loading">Loading flags…</div>;
  }

  return (
    <table className="flag-list">
      <thead>
        <tr>
          <th>Key</th>
          <th>Rollout</th>
          <th>Rules</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {flags.map((flag) => (
          <tr key={flag.id} className={flag.enabled ? "" : "is-disabled"}>
            <td>
              <a onClick={() => onSelect(flag)}>{flag.key}</a>
              <div className="flag-list__description">{flag.description}</div>
            </td>
            <td>{flag.rollout_percentage}%</td>
            <td>{flag.rules.length}</td>
            <td>
              <button onClick={() => toggle(flag)}>
                {flag.enabled ? "Disable" : "Enable"}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
