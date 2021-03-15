import React, { useState } from "react";

import FlagDetail from "./components/FlagDetail";
import FlagList from "./components/FlagList";
import { Flag } from "./types";

export default function App() {
  const [selected, setSelected] = useState<Flag | null>(null);

  return (
    <div className="app">
      <header className="app__header">
        <h1>Switchboard</h1>
      </header>

      <main className="app__main">
        {selected ? (
          <>
            <button onClick={() => setSelected(null)}>&larr; All flags</button>
            <FlagDetail flag={selected} />
          </>
        ) : (
          <FlagList onSelect={setSelected} />
        )}
      </main>
    </div>
  );
}
