import { MONO } from "./theme";

/** A styled stretch of text; a line is a list of runs. */
export type Run = { text: string; color?: string; weight?: number; italic?: boolean; mono?: boolean };

export const runsLength = (runs: Run[]) => runs.reduce((length, run) => length + run.text.length, 0);

/** The first `chars` characters of `runs`, each keeping its style. */
export const sliceRuns = (runs: Run[], chars: number): Run[] => {
  const sliced: Run[] = [];
  let remaining = chars;
  for (const run of runs) {
    if (remaining <= 0) break;
    sliced.push({ ...run, text: run.text.slice(0, remaining) });
    remaining -= run.text.length;
  }
  return sliced;
};

/** Renders runs as spans; unset styles inherit from the parent, so wrap to set size or family. */
export const Runs: React.FC<{ runs: Run[] }> = ({ runs }) => (
  <>
    {runs.map((run, i) => (
      <span
        key={i}
        style={{
          color: run.color,
          fontWeight: run.weight,
          fontStyle: run.italic ? "italic" : undefined,
          fontFamily: run.mono ? MONO : undefined,
        }}
      >
        {run.text}
      </span>
    ))}
  </>
);
