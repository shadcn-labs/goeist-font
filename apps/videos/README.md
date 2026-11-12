# Goeist launch video

A 20 second, 1920×1080, 60 fps launch video for Goeist, made with [Remotion](https://www.remotion.dev). It renders the variable fonts from `fonts/` in the repository root; run `make build` there first if they are missing.

## Usage

Requires Node 22 (`.nvmrc`) and pnpm.

```sh
cd apps/videos
pnpm install
pnpm dev      # Remotion Studio: scrub the timeline and preview edits live
pnpm render   # writes out/goeist-launch.mp4
```

Both commands first copy the fonts into `public/fonts/`; `pnpm fonts` does only that step.

## Editing

- `src/script.ts`: caption lines, specimen strings and the install command.
- `src/timeline.ts`: when each beat starts, typing speed and caret blink.
- `src/theme.ts`: colors, sizes and positions.
- `src/scenes/`: one file per bottom-row beat: `Intro`, `Shuffle` (glyph count), `Weight`, `Italic` and `Command` (Goeist Mono).
- `src/components/Soundtrack.tsx` and `src/sfx.ts`: where each sound plays and how loud (see [Sound](#sound)).

The glyph count in the caption is read from the staged `Goeist-Variable.ttf`, so it always matches the current build.

## Sound

Every sound sits on the frame of what causes it. The scenes export their cue frames (`DOT_CUE`, `INTRO_CUES`, `SETTLE_CUES`, `THIN_CUE`, `BLACK_CUE`, `LEAN_CUE`, `COMMAND_KEYS`) and `src/typewriter.ts` lists every caption keystroke; `src/components/Soundtrack.tsx` places the sounds on them and sets every level, so retiming the picture moves its sound too.

- Typing uses one laptop keyboard. Caption typing is faster than any typist, so a key sounds at most 12 times a second.
- The intro letters play a C major pentatonic marimba run; the shuffled glyphs get a card riffle, and each slot locks with a rising wood tick.
- Thin to Black is the loudest moment: a reversed crash pulls into a kick and a low marimba C.
- The film ends on a soft marimba C and G that rings out under the fade.

The mix is effects only (no music bed): about −21 LUFS integrated, true peak −2.6 dBTP after AAC encoding.

To swap a sound, put a WAV in `public/sfx/`, register it in `src/sfx.ts` with its anchor (seconds from the file start to its attack, or to the peak for swells and swishes) and set its gain in `Soundtrack.tsx`.

### Sound credits

Every recording is [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) on Freesound (licences read on each sound's page). Edits: trimmed with short cosine fades, folded to mono except `swoosh`, `whip` and `rise`, transient-limited where noted, peak-normalised to −1 dBFS, 48 kHz/16-bit.

| File | Source | Edit |
| --- | --- | --- |
| `key-01` … `key-12`, `key-space` | [Laptop Keyboard](https://freesound.org/people/bassboybg/sounds/346589/) by bassboybg | 13 keystrokes sliced from one slow take, limited 8 dB |
| `pop` | [Pop sound](https://freesound.org/people/deraj/sounds/202230/) by deraj | from the attack, limited 4 dB |
| `breath` | [Whosh - Reversed/Reverbed breath](https://freesound.org/people/PrdiChlp/sounds/181889/) by PrdiChlp | 0.9–2.3 s |
| `riffle` | [Shuffling cards (riffle) 03](https://freesound.org/people/VKProduktion/sounds/217503/) by VKProduktion | 0.1–1.65 s, −5 dB shelf above 5 kHz, limited 9 dB |
| `wood` | [wood block](https://freesound.org/people/thomasjaunism/sounds/218461/) by thomasjaunism | limited 4 dB |
| `swoosh` | [swoosh](https://freesound.org/people/Halgrimm/sounds/169867/) by Halgrimm | 0.2–2.3 s, limited 3 dB |
| `whip` | [whip02](https://freesound.org/people/snowflakes/sounds/72190/) by snowflakes | limited 4 dB |
| `rise` | [Rpeople_RevCrash2](https://freesound.org/people/rhythmpeople/sounds/165154/) by rhythmpeople | last 1.25 s |
| `kick` | [Kick Drum](https://freesound.org/people/Poligonstudio/sounds/410149/) by Poligonstudio | limited 4 dB |
| `marimba-c3`, `-c5`, `-g5`, `-b5` | VSCO 2 CE marimba by sgossner (Versilian Studios): [C3](https://freesound.org/people/sgossner/sounds/373579/), [C5](https://freesound.org/people/sgossner/sounds/373580/), [G5](https://freesound.org/people/sgossner/sounds/373586/) (titled F#5, measures G5), [B5](https://freesound.org/people/sgossner/sounds/373578/) | trimmed, limited 5 dB |

## License

Remotion is free for individuals and companies of up to three people; larger companies need a [Company License](https://www.remotion.dev/docs/license/pricing).
