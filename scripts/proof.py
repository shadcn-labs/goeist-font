#!/usr/bin/env python3
"""Generate a self-contained, offline browser specimen and complete SVG atlases.

  python scripts/proof.py --family GoistMono
  python -m http.server 8000  # from repository root; open /out/GoistMono/proof/

No CDN, JavaScript dependency, system-font substitute, or rasterized glyph subset
is used. The text panels load both genuine variable styles; glyph atlases contain
all exported glyphs, including unencoded alternates, at every static weight and
at intermediate variable weights 250/550/850.
"""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from families import FAMILIES

WEIGHTS = tuple(range(100, 901, 100))
INTERMEDIATES = (250, 550, 850)


def relative_url(path, output):
    return "/".join(Path(os.path.relpath(path.resolve(), output.resolve())).parts)


def style_of(font):
    return "italic" if font["OS/2"].fsSelection & 1 else "upright"


def atlas(font, weight=None):
    location = {"wght": weight} if weight is not None and "fvar" in font else None
    glyphs = font.getGlyphSet(location=location)
    reverse = {}
    for cp, name in sorted(font.getBestCmap().items()):
        reverse.setdefault(name, []).append(cp)
    rows = []
    for name in font.getGlyphOrder():
        pen = SVGPathPen(glyphs)
        bounds = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        glyphs[name].draw(bounds)
        rows.append({"name": name, "codepoints": reverse.get(name, []),
                     "advance": glyphs[name].width, "bounds": bounds.bounds,
                     "path": pen.getCommands()})
    return {"upm": font["head"].unitsPerEm,
            "ascender": font["hhea"].ascent, "descender": font["hhea"].descent,
            "glyphs": rows}


PAGE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__FAMILY__ · The round side of __UPSTREAM__</title>
<style>
:root{color-scheme:light;--paper:#f6f5f1;--ink:#202321;--muted:#696e67;--line:#d8ddd3;--accent:#356343;--soft:#e8eedf}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 ui-sans-serif,system-ui,sans-serif}main{max-width:1480px;margin:auto;padding:38px 5vw 90px}header{display:flex;justify-content:space-between;gap:30px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:28px}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:11px;color:var(--accent)}h1{font-size:clamp(54px,10vw,120px);line-height:1;margin:12px 0 18px;font-weight:500;letter-spacing:-.06em}h2{font-size:24px;font-weight:500;letter-spacing:-.03em;margin:0}p{max-width:66ch}.muted,.meta{color:var(--muted)}.badge{display:inline-block;border:1px solid var(--line);padding:6px 12px;border-radius:20px;white-space:nowrap}.status{max-width:420px}.status[data-state=error]{color:#a02424}.controls{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:18px;padding:24px 0}label{display:block;font-size:12px;color:var(--muted)}label strong{color:var(--ink);font-weight:500}input,select,textarea,button{font:inherit}input[type=range]{width:100%;accent-color:var(--accent)}select,input[type=search]{border:1px solid var(--line);background:transparent;border-radius:8px;padding:8px 10px;width:100%;color:var(--ink)}textarea{width:100%;resize:vertical;min-height:110px;border:1px solid var(--line);background:#ffffff80;border-radius:12px;padding:16px;line-height:1.45}button{border:1px solid var(--line);background:white;border-radius:8px;padding:9px 14px;cursor:pointer}.features{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 24px}.features label{border:1px solid var(--line);border-radius:20px;padding:5px 10px;color:var(--ink);cursor:pointer}.features label:has(input:checked){background:var(--soft);border-color:var(--accent)}.features input{accent-color:var(--accent)}.section-head{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:42px 0 20px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:1px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--line)}.panel{background:var(--paper);padding:24px;min-width:0}.panel .meta{font-size:11px;letter-spacing:.1em;text-transform:uppercase}.live-text{font-size:var(--size,64px);line-height:1.22;letter-spacing:-.025em;overflow-wrap:anywhere;white-space:pre-wrap;margin-top:20px;min-height:190px}.goist{font-family:GoistProof}.geist{font-family:GeistProof}.needs-font:not(.ready){visibility:hidden}.coverage{font-size:12px;color:#9b4618;padding-top:10px}.waterfall{border-top:1px solid var(--line)}.water-row{display:grid;grid-template-columns:40px 1fr;gap:16px;padding:10px 0;border-bottom:1px solid var(--line);align-items:baseline}.water-row span:first-child{font:11px ui-monospace,monospace;color:var(--muted)}.water-text{overflow:hidden;white-space:nowrap;line-height:1.45}.script-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.script-card{border:1px solid var(--line);padding:20px;border-radius:12px;min-width:0}.script-card .goist{font-size:27px;overflow-wrap:anywhere;line-height:1.6}.atlas-tools{display:grid;grid-template-columns:1fr 2fr auto;gap:14px;align-items:end}.glyph-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:18px 0}.glyph{background:var(--paper);min-width:0;padding:12px}.glyph svg{display:block;width:100%;height:100px;overflow:visible}.glyph b{display:block;overflow-wrap:anywhere;font:11px ui-monospace,monospace}.glyph small{display:block;font-size:9px;color:var(--muted);overflow-wrap:anywhere}.atlas-note{font-size:12px;color:var(--muted)}.detail{font-size:12px;color:var(--muted);padding:18px;border-left:2px solid var(--accent)}footer{border-top:1px solid var(--line);margin-top:60px;padding-top:20px;font-size:12px;color:var(--muted)}@media(max-width:760px){main{padding:24px 20px 60px}header,.section-head{display:block}.controls{grid-template-columns:1fr 1fr}.comparison,.script-grid{grid-template-columns:1fr}.atlas-tools{grid-template-columns:1fr}.status{margin-top:20px}}
</style>
<main>
<header><div><div class="eyebrow">__FAMILY__ by __AUTHOR__ · Optical proof</div><h1 class="goist needs-font">__FAMILY__</h1><p class="muted">The familiar skeleton, a softer finish. Explore nine weights, genuine italics, every stylistic set, and the complete exported glyph repertoire.</p></div><div class="status"><span class="badge">100 — 900 · Upright + Italic</span><p id="status" role="status">Loading local variable fonts…</p><p class="muted">Run a local HTTP server from the repository root. No network assets are requested.</p></div></header>
<div class="controls"><label>Style<select id="style"><option value="upright">Upright</option><option value="italic">Italic</option></select></label><label>Weight <strong id="weight-value">400</strong><input id="weight" type="range" min="100" max="900" step="1" value="400"></label><label>Size <strong id="size-value">64 px</strong><input id="size" type="range" min="12" max="180" value="64"></label><label>Language<select id="language"><option value="en">English / Latin</option><option value="ru">Russian</option><option value="bg">Bulgarian</option><option value="sr">Serbian</option><option value="mk">Macedonian</option></select></label></div>
<label for="text">Your text · all changes apply to both fonts</label><textarea id="text" spellcheck="false">Hamburgefontsiv
A quieter kind of familiar. 0123456789</textarea><div class="features" id="features"></div><div class="coverage" id="coverage" role="status"></div>
<div class="section-head"><h2>Same words. Different endings.</h2><span class="muted">Actual variable webfont vs official original release</span></div><div class="comparison"><div class="panel"><div class="meta">__FAMILY__ · Rounded</div><div id="rounded" class="live-text goist needs-font"></div></div><div class="panel"><div class="meta">__UPSTREAM__ · Original release</div><div id="original" class="live-text geist needs-font"></div></div></div>
<p class="detail">The original panel uses the immutable official release binaries; their version is not assumed identical to the pinned editable source. See the separate verification report for exact source/release drift. This page is a visual proof, not an automated validation claim.</p>
<div class="section-head"><h2>Reading sizes</h2><span class="muted">12 / 14 / 16 / 20 / 24 / 32 / 48 / 72 px</span></div><div class="waterfall" id="waterfall"></div>
<div class="section-head"><h2>Scripts, accents &amp; symbols</h2><span class="muted">Select a language above to inspect Cyrillic localization</span></div><div class="script-grid" id="scripts"></div>
<div class="section-head"><h2>Every glyph, not just Unicode</h2><span class="muted" id="glyph-count"></span></div><div class="atlas-tools"><label>Outline atlas<select id="atlas"></select></label><label>Find glyph / U+ code / character<input id="search" type="search" placeholder="a.ss01, 0041, € …"></label><button id="more">Show more</button></div><p class="atlas-note">SVG paths are extracted directly from built fonts. All exported unencoded alternates, ligatures, combining marks and components are included; no browser font fallback is involved. Atlases cover all nine static weights in each style and variable instances at 250, 550 and 850. Cells share vertical metrics; unusually wide glyphs are fitted to their advance.</p><div id="atlas-status" role="status"></div><div class="glyph-grid" id="glyphs"></div>
<footer>__FAMILY__ by __AUTHOR__, developed under Shadcn Labs · Upstream credit: Vercel __UPSTREAM__ and its contributors · SIL Open Font License 1.1. __FAMILY__ is an independent project, not affiliated with or endorsed by Vercel, Inc. Vercel and related marks are trademarks of Vercel, Inc. Font loading and coverage messages are local runtime observations; consult <a href="../verification.json">verification.json</a> for the separate programmatic audit.</footer>
</main><script id="manifest" type="application/json">__MANIFEST__</script>
<script>
'use strict';
const manifest=JSON.parse(document.querySelector('#manifest').textContent);
const $=s=>document.querySelector(s);
const state={loaded:new Set(),failures:{},limit:180,atlas:null,atlasRequest:0};
const featureTags=[...Array.from({length:11},(_,i)=>`ss${String(i+1).padStart(2,'0')}`),'tnum','frac','liga','kern','mark','mkmk','locl'];
for(const tag of featureTags){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=tag;input.checked=['liga','kern','mark','mkmk','locl'].includes(tag);input.addEventListener('change',update);label.append(input,document.createTextNode(' '+tag));$('#features').append(label)}
const scriptSamples=[['Latin · extended','ÀÁÂÃÄÅ ÇĆČ ĐÈÉÊË ĞĢ Īİ ŁŃÑ ŐÖ ŘŠ ŤŰÜ ŴÝŸ Ž\nàáâãäå çćč đèéêë ğģ īı łńñ őö řš ťűü ŵýÿ ž'],['Diacritics · composed / decomposed','Ångström naïve façade piñata\nA\u030a e\u0301 o\u0308 n\u0303 c\u0327 a\u0301\u0323'],['Cyrillic · localization','БГДЛПТ бвгдпт Ѓѓ Ќќ\nЂђ Љљ Њњ Ћћ Џџ'],['Figures · fractions · ligatures','0123456789 1/2 3/4 11/16\noffice affine ffi ffl fi fl'],['Currencies','€ $ ¢ £ ¤ ¥ ₴ ₽ ₺ ₹'],['Math · punctuation','+ − × ÷ = ≠ ≤ ≥ ± ∞ ∑ ∏ √ ∫\n“Round.” ‘Warm.’ (Quiet) [Clear] {Goist}'],['Code','const round = (r) => r >= 0.5;\nif (a != b && i++ <= 10) { return [0x1F, "ok"]; }']];
for(const [title,text] of scriptSamples){const card=document.createElement('div');card.className='script-card';const label=document.createElement('div');label.className='meta';label.textContent=title;const specimen=document.createElement('div');specimen.className='goist needs-font supplemental';specimen.textContent=text;card.append(label,specimen);$('#scripts').append(card)}
for(const size of [12,14,16,20,24,32,48,72]){const row=document.createElement('div');row.className='water-row';const label=document.createElement('span');label.textContent=size;const text=document.createElement('span');text.className='water-text goist needs-font';text.style.fontSize=size+'px';text.textContent='The quick brown fox jumps over the lazy dog. Hamburgefontsiv 0123456789';row.append(label,text);$('#waterfall').append(row)}
for(const item of manifest.atlases){const option=document.createElement('option');option.value=item.url;option.textContent=item.label;$('#atlas').append(option)}
$('#atlas').value=manifest.atlases.find(a=>a.style==='upright'&&a.weight===400).url;
function selectedStyle(){return $('#style').value}
function covered(style,reference=false){return new Set(manifest.fonts[style][reference?'reference':'goist'].cmap)}
function missingText(text,cmap){return [...new Set([...text].filter(c=>!['\n','\r','\t'].includes(c)&&!cmap.has(c.codePointAt(0))))]}
function cp(c){return 'U+'+c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')}
function renderCovered(node,text,cmap){node.replaceChildren();let run='';function flush(){if(run){node.append(document.createTextNode(run));run=''}}for(const character of text){if(cmap.has(character.codePointAt(0))||['\n','\r','\t'].includes(character)){run+=character}else{flush();const missing=document.createElement('span');missing.textContent='['+cp(character)+']';missing.title='Unsupported character, not a font glyph';missing.style.cssText='font:11px ui-monospace,monospace;color:#9b4618;letter-spacing:0';node.append(missing)}}flush()}
function update(){const style=selectedStyle(),fontStyle=style==='italic'?'italic':'normal',weight=$('#weight').value,size=$('#size').value,language=$('#language').value,text=$('#text').value;$('#weight-value').textContent=weight;$('#size-value').textContent=size+' px';const features=[...$('#features').querySelectorAll('input')].map(i=>`"${i.value}" ${i.checked?1:0}`).join(', ');
for(const node of document.querySelectorAll('.goist,.geist')){node.style.fontStyle=fontStyle;node.style.fontWeight=weight;node.style.fontVariationSettings=`"wght" ${weight}`;node.style.fontFeatureSettings=features;node.style.fontSynthesis='none';node.lang=language;node.classList.toggle('ready',state.loaded.has(style))}
for(const id of ['#rounded','#original']){renderCovered($(id),text,covered(style,id==='#original'));$(id).style.setProperty('--size',size+'px')}
const roundedMissing=missingText(text,covered(style)),originalMissing=missingText(text,covered(style,true));const warnings=[];if(roundedMissing.length)warnings.push('__FAMILY__ unsupported: '+roundedMissing.map(cp).join(' '));if(originalMissing.length)warnings.push('Original unsupported: '+originalMissing.map(cp).join(' '));$('#coverage').textContent=warnings.length?warnings.join(' · ')+'. Explicit codepoint labels replace missing characters; no fallback glyphs are displayed.':'Custom text is covered by both repertoires; font load status is shown above.';
for(const node of document.querySelectorAll('.supplemental')){node.dataset.originalText??=node.textContent;renderCovered(node,node.dataset.originalText,covered(style));node.title='Unsupported characters, if any, appear as explicit codepoint labels rather than fallback glyphs.'}
const loaded=state.loaded.has(style),failure=state.failures[style];$('#status').textContent=loaded?`Local ${style} __FAMILY__ WOFF2 and original __UPSTREAM__ TTF loaded. Font synthesis disabled.`:failure?`Font load failed for ${style}: ${failure}. Text proof is hidden.`:`Loading ${style} fonts…`;$('#status').dataset.state=loaded?'ready':failure?'error':'loading'}
async function loadFonts(){for(const [style,entry] of Object.entries(manifest.fonts)){try{for(const [kind,family] of [['goist','GoistProof'],['reference','GeistProof']]){const face=new FontFace(family,`url("${entry[kind].url}")`,{style:style==='italic'?'italic':'normal',weight:'100 900',display:'block'});await face.load();document.fonts.add(face)}state.loaded.add(style);update()}catch(error){state.failures[style]=error.message;update();console.error(error)}}}
const ns='http://www.w3.org/2000/svg';
function renderAtlas(){if(!state.atlas)return;const query=$('#search').value.trim().toLowerCase().replace(/^u\+/,'');const matches=state.atlas.glyphs.filter(g=>!query||g.name.toLowerCase().includes(query)||g.codepoints.some(n=>n.toString(16).padStart(4,'0').includes(query)||String.fromCodePoint(n).toLowerCase()===query));$('#glyph-count').textContent=`${matches.length} / ${state.atlas.glyphs.length} glyphs`;$('#glyphs').replaceChildren();const upm=state.atlas.upm;for(const glyph of matches.slice(0,state.limit)){const cell=document.createElement('div');cell.className='glyph';const svg=document.createElementNS(ns,'svg');const top=Math.max(state.atlas.ascender,upm*.95),bottom=Math.min(state.atlas.descender,-upm*.25),width=Math.max(glyph.advance,upm*.85);svg.setAttribute('viewBox',`${-upm*.12} ${-top} ${width+upm*.24} ${top-bottom}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',glyph.name);const path=document.createElementNS(ns,'path');path.setAttribute('d',glyph.path);path.setAttribute('transform','scale(1,-1)');path.setAttribute('fill','currentColor');const baseline=document.createElementNS(ns,'path');baseline.setAttribute('d',`M ${-upm*.1} 0 H ${width+upm*.1}`);baseline.setAttribute('stroke','#d8ddd3');baseline.setAttribute('stroke-width','3');svg.append(baseline,path);const name=document.createElement('b');name.textContent=glyph.name;const unicode=document.createElement('small');unicode.textContent=glyph.codepoints.length?glyph.codepoints.map(n=>'U+'+n.toString(16).toUpperCase().padStart(4,'0')).join(' '):'Unencoded';const metrics=document.createElement('small');metrics.textContent=`Advance ${Math.round(glyph.advance*100)/100}`;cell.append(svg,name,unicode,metrics);$('#glyphs').append(cell)}$('#more').disabled=matches.length<=state.limit;$('#more').textContent=matches.length<=state.limit?'All shown':`Show ${Math.min(180,matches.length-state.limit)} more`}
async function loadAtlas(){const request=++state.atlasRequest;$('#atlas-status').textContent='Loading complete outline atlas…';try{const response=await fetch($('#atlas').value);if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();if(request!==state.atlasRequest)return;state.atlas=data;state.limit=180;$('#atlas-status').textContent='';renderAtlas()}catch(error){if(request!==state.atlasRequest)return;$('#atlas-status').textContent=`Atlas unavailable: ${error.message}. Serve the repository with HTTP, not file://.`}}
for(const id of ['#style','#weight','#size','#language','#text'])$(id).addEventListener('input',update);$('#atlas').addEventListener('change',loadAtlas);$('#search').addEventListener('input',()=>{state.limit=180;renderAtlas()});$('#more').addEventListener('click',()=>{state.limit+=180;renderAtlas()});update();loadFonts();loadAtlas();
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", default="Goist", choices=sorted(FAMILIES))
    parser.add_argument("--fonts", type=Path, help="default: fonts/<family>")
    parser.add_argument("--reference", type=Path, help="default: sources/<family>/upstream/reference")
    parser.add_argument("--output", type=Path, help="default: out/<family>/proof")
    args = parser.parse_args()
    family = FAMILIES[args.family]
    args.fonts = args.fonts or Path("fonts") / family.key
    args.reference = args.reference or Path("sources") / family.key / "upstream/reference"
    args.output = args.output or Path("out") / family.key / "proof"
    author_file = Path(__file__).resolve().parent.parent / "AUTHORS.txt"
    author_record = next((line.strip() for line in author_file.read_text(encoding="utf-8").splitlines()
                          if line.strip() and not line.lstrip().startswith("#")), "")
    author = author_record.partition("<")[0].strip()
    if not author:
        parser.error("AUTHORS.txt must identify the Goist author")
    args.output.mkdir(parents=True, exist_ok=True)
    atlas_dir = args.output / "atlases"
    atlas_dir.mkdir(exist_ok=True)
    manifest = {"fonts": {}, "atlases": []}
    variables = {}
    for path in sorted((args.fonts / "variable").glob("*.ttf")):
        with TTFont(path) as font:
            if "fvar" in font:
                style = style_of(font)
                if style in variables:
                    parser.error(f"Multiple {style} variable fonts in {args.fonts / 'variable'}")
                variables[style] = path
                web = args.fonts / "webfonts" / (path.stem + ".woff2")
                if not web.is_file():
                    parser.error(f"Missing actual variable WOFF2: {web}")
                manifest["fonts"][style] = {"goist": {"url": relative_url(web, args.output),
                                                              "cmap": sorted(font.getBestCmap())}}
    references = {}
    for path in sorted(args.reference.rglob("*.ttf")):
        with TTFont(path) as font:
            if "fvar" in font:
                style = style_of(font)
                if style in references:
                    parser.error(f"Multiple {style} reference variable fonts")
                references[style] = path
                if style in manifest["fonts"]:
                    manifest["fonts"][style]["reference"] = {
                        "url": relative_url(path, args.output), "cmap": sorted(font.getBestCmap())}
    if set(variables) != {"upright", "italic"} or set(references) != {"upright", "italic"}:
        parser.error(f"Both genuine upright and italic variable fonts are required for {family.name} "
                     f"and original {family.upstream_label}")
    static_keys = set()
    for path in sorted((args.fonts / "ttf").glob("*.ttf")):
        with TTFont(path) as font:
            if "fvar" in font:
                continue
            style, weight = style_of(font), int(font["OS/2"].usWeightClass)
            key = (style, weight)
            if key in static_keys:
                parser.error(f"Duplicate static style: {style} {weight}")
            static_keys.add(key)
            filename = f"{style}-{weight}.json"
            (atlas_dir / filename).write_text(json.dumps(atlas(font), separators=(",", ":")))
            manifest["atlases"].append({"label": f"{style.title()} · {weight} · static TTF",
                                        "style": style, "weight": weight, "url": f"atlases/{filename}"})
    expected = {(style, weight) for style in ("upright", "italic") for weight in WEIGHTS}
    if static_keys != expected:
        parser.error(f"All 18 static weights are required; missing: {sorted(expected - static_keys)}")
    for style, path in variables.items():
        with TTFont(path) as font:
            for weight in INTERMEDIATES:
                filename = f"{style}-{weight}-variable.json"
                (atlas_dir / filename).write_text(json.dumps(atlas(font, weight), separators=(",", ":")))
                manifest["atlases"].append({"label": f"{style.title()} · {weight} · variable instance",
                                            "style": style, "weight": weight,
                                            "url": f"atlases/{filename}"})
    manifest["atlases"].sort(key=lambda a: (a["style"] == "italic", a["weight"]))
    encoded = json.dumps(manifest, ensure_ascii=True).replace("<", "\\u003c")
    page = (PAGE.replace("__AUTHOR__", html.escape(author)).replace("__MANIFEST__", encoded)
            .replace("__FAMILY__", html.escape(family.name)).replace("__UPSTREAM__", html.escape(family.upstream_label)))
    (args.output / "index.html").write_text(page)
    print(f"Generated {args.output / 'index.html'} and {len(manifest['atlases'])} full-glyph atlases.")
    print("Serve the repository root with HTTP, then open /" + relative_url(args.output, Path.cwd()) + "/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
