#!/usr/bin/env python3
"""Generate a self-contained, offline browser specimen and complete SVG atlases.

  python scripts/proof.py --family GoeistMono
  python -m http.server 8000  # from repository root; open /out/GoeistMono/proof/

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

INTERMEDIATES = (250, 550, 850)


def relative_url(path, output):
    return "/".join(Path(os.path.relpath(path.resolve(), output.resolve())).parts)


def style_of(font):
    return "italic" if font["OS/2"].fsSelection & 1 else "upright"


def atlas(font, location=None):
    glyphs = font.getGlyphSet(location=location if location and "fvar" in font else None)
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
    os2 = font["OS/2"]
    return {"upm": font["head"].unitsPerEm,
            "ascender": font["hhea"].ascent, "descender": font["hhea"].descent,
            "metrics": {"cap height": os2.sCapHeight, "x-height": os2.sxHeight, "baseline": 0,
                        "ascender": os2.sTypoAscender, "descender": os2.sTypoDescender},
            "glyphs": rows}


PAGE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__FAMILY__ · The round side of __UPSTREAM__</title>
<style>
:root{color-scheme:light;--paper:#f6f5f1;--ink:#202321;--muted:#696e67;--line:#d8ddd3;--accent:#356343;--soft:#e8eedf}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 ui-sans-serif,system-ui,sans-serif}main{max-width:1480px;margin:auto;padding:38px 5vw 90px}header{display:flex;justify-content:space-between;gap:30px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:28px}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:11px;color:var(--accent)}h1{font-size:clamp(54px,10vw,120px);line-height:1;margin:12px 0 18px;font-weight:500;letter-spacing:-.06em}h2{font-size:24px;font-weight:500;letter-spacing:-.03em;margin:0}p{max-width:66ch}.muted,.meta{color:var(--muted)}.badge{display:inline-block;border:1px solid var(--line);padding:6px 12px;border-radius:20px;white-space:nowrap}.status{max-width:420px}.status[data-state=error]{color:#a02424}.controls{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:18px;padding:24px 0}label{display:block;font-size:12px;color:var(--muted)}label strong{color:var(--ink);font-weight:500}input,select,textarea,button{font:inherit}input[type=range]{width:100%;accent-color:var(--accent)}select,input[type=search]{border:1px solid var(--line);background:transparent;border-radius:8px;padding:8px 10px;width:100%;color:var(--ink)}textarea{width:100%;resize:vertical;min-height:110px;border:1px solid var(--line);background:#ffffff80;border-radius:12px;padding:16px;line-height:1.45}button{border:1px solid var(--line);background:white;border-radius:8px;padding:9px 14px;cursor:pointer}.features{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 24px}.features label{border:1px solid var(--line);border-radius:20px;padding:5px 10px;color:var(--ink);cursor:pointer}.features label:has(input:checked){background:var(--soft);border-color:var(--accent)}.features input{accent-color:var(--accent)}.section-head{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:42px 0 20px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:1px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--line)}.panel{background:var(--paper);padding:24px;min-width:0}.panel .meta{font-size:11px;letter-spacing:.1em;text-transform:uppercase}.live-text{font-size:var(--size,64px);line-height:1.22;letter-spacing:-.025em;overflow-wrap:anywhere;white-space:pre-wrap;margin-top:20px;min-height:190px}.goeist{font-family:GoeistProof}.geist{font-family:GeistProof}.needs-font:not(.ready){visibility:hidden}.coverage{font-size:12px;color:#9b4618;padding-top:10px}.waterfall{border-top:1px solid var(--line)}.water-row{display:grid;grid-template-columns:40px 1fr;gap:16px;padding:10px 0;border-bottom:1px solid var(--line);align-items:baseline}.water-row span:first-child{font:11px ui-monospace,monospace;color:var(--muted)}.water-text{overflow:hidden;white-space:nowrap;line-height:1.45}.script-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.script-card{border:1px solid var(--line);padding:20px;border-radius:12px;min-width:0}.script-card .goeist{font-size:27px;overflow-wrap:anywhere;line-height:1.6}.atlas-tools{display:grid;grid-template-columns:1fr 2fr auto;gap:14px;align-items:end}.glyph-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:18px 0}.glyph{background:var(--paper);min-width:0;padding:12px}.glyph svg{display:block;width:100%;height:100px;overflow:visible}.glyph b{display:block;overflow-wrap:anywhere;font:11px ui-monospace,monospace}.glyph small{display:block;font-size:9px;color:var(--muted);overflow-wrap:anywhere}.atlas-note{font-size:12px;color:var(--muted)}.detail{font-size:12px;color:var(--muted);padding:18px;border-left:2px solid var(--accent)}footer{border-top:1px solid var(--line);margin-top:60px;padding-top:20px;font-size:12px;color:var(--muted)}@media(max-width:760px){main{padding:24px 20px 60px}header,.section-head{display:block}.controls{grid-template-columns:1fr 1fr}.comparison,.script-grid{grid-template-columns:1fr}.atlas-tools{grid-template-columns:1fr}.status{margin-top:20px}}
.metrics svg{display:block;width:100%;height:auto;max-height:520px;color:var(--ink)}.spacing{border-top:1px solid var(--line)}.spacing-line{font-size:48px;line-height:1.5;white-space:nowrap;overflow:hidden;border-bottom:1px solid var(--line)}.charset{font-size:30px;line-height:1.6;overflow-wrap:anywhere}.charset span{display:inline-block;min-width:1.3em;text-align:center}
</style>
<main>
<header><div><div class="eyebrow">__FAMILY__ by __AUTHOR__ · Optical proof</div><h1 class="goeist needs-font">__FAMILY__</h1><p class="muted">The familiar skeleton, a softer finish. __INTRO__</p></div><div class="status"><span class="badge">__BADGE__</span><p id="status" role="status">Loading local variable fonts…</p><p class="muted">Run a local HTTP server from the repository root. No network assets are requested.</p></div></header>
<div class="controls"><label>Style<select id="style"></select></label><label>__AXIS_LABEL__ <strong id="weight-value">__AXIS_DEFAULT__</strong><input id="weight" type="range" min="__AXIS_MIN__" max="__AXIS_MAX__" step="__AXIS_STEP__" value="__AXIS_DEFAULT__"></label><label>Size <strong id="size-value">64 px</strong><input id="size" type="range" min="12" max="180" value="64"></label><label>Language<select id="language"><option value="en">English / Latin</option><option value="ru">Russian</option><option value="bg">Bulgarian</option><option value="sr">Serbian</option><option value="mk">Macedonian</option></select></label></div>
<label for="text">Your text · all changes apply to both fonts</label><textarea id="text" spellcheck="false">Hamburgefontsiv
A quieter kind of familiar. 0123456789</textarea><div class="features" id="features"></div><div class="coverage" id="coverage" role="status"></div>
<div class="section-head"><h2>Same words. Different endings.</h2><span class="muted">Actual variable webfont vs official original release</span></div><div class="comparison"><div class="panel"><div class="meta">__FAMILY__ · Rounded</div><div id="rounded" class="live-text goeist needs-font"></div></div><div class="panel"><div class="meta">__UPSTREAM__ · Original release</div><div id="original" class="live-text geist needs-font"></div></div></div>
<p class="detail">The original panel uses the immutable official release binaries; their version is not assumed identical to the pinned editable source. See the separate verification report for exact source/release drift. This page is a visual proof, not an automated validation claim.</p>
<div class="section-head"><h2>Reading sizes</h2><span class="muted">12 / 14 / 16 / 20 / 24 / 32 / 48 / 72 px</span></div><div class="waterfall" id="waterfall"></div>
<div class="section-head"><h2>Vertical metrics</h2><span class="muted">Outlines and lines from the selected atlas's font file</span></div><div id="metrics" class="metrics"></div>
<div class="section-head"><h2>Spacing</h2><span class="muted">48 px, kerning on: curved letters should sit as evenly between n and H as straight ones</span></div><div id="spacing" class="spacing"></div>
<div class="section-head"><h2>Character set</h2><span class="muted" id="charset-count"></span></div><div id="charset" class="charset goeist needs-font"></div>
<div class="section-head"><h2>Scripts, accents &amp; symbols</h2><span class="muted">Select a language above to inspect Cyrillic localization</span></div><div class="script-grid" id="scripts"></div>
<div class="section-head"><h2>Every glyph, not just Unicode</h2><span class="muted" id="glyph-count"></span></div><div class="atlas-tools"><label>Outline atlas<select id="atlas"></select></label><label>Find glyph / U+ code / character<input id="search" type="search" placeholder="a.ss01, 0041, € …"></label><button id="more">Show more</button></div><p class="atlas-note">SVG paths are extracted directly from built fonts. All exported unencoded alternates, ligatures, combining marks and components are included; no browser font fallback is involved. __ATLAS_NOTE__ Cells share vertical metrics; unusually wide glyphs are fitted to their advance.</p><div id="atlas-status" role="status"></div><div class="glyph-grid" id="glyphs"></div>
<footer>__FAMILY__ by __AUTHOR__, developed under Shadcn Labs · Upstream credit: Vercel __UPSTREAM__ and its contributors · SIL Open Font License 1.1. __FAMILY__ is independent, not affiliated with or endorsed by <a href="https://vercel.com/geist/brands#usage">Vercel</a> or <a href="https://abcdinamo.com/licenses">Dinamo</a>. ABC Diatype is a visual reference only; none of its font data is used. Vercel, the Vercel design, Next.js and related marks, designs and logos are trademarks or registered trademarks of Vercel, Inc. or its affiliates in the US and other countries. Font loading and coverage messages are local runtime observations; consult <a href="../verification.json">verification.json</a> for the separate programmatic audit.</footer>
</main><script id="manifest" type="application/json">__MANIFEST__</script>
<script>
'use strict';
const manifest=JSON.parse(document.querySelector('#manifest').textContent);
const $=s=>document.querySelector(s);
const state={loaded:new Set(),failures:{},limit:180,atlas:null,atlasRequest:0};
const featureTags=[...Array.from({length:11},(_,i)=>`ss${String(i+1).padStart(2,'0')}`),'tnum','frac','liga','kern','mark','mkmk','locl'];
for(const tag of featureTags){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.value=tag;input.checked=['liga','kern','mark','mkmk','locl'].includes(tag);input.addEventListener('change',update);label.append(input,document.createTextNode(' '+tag));$('#features').append(label)}
const scriptSamples=[['Latin · extended','ÀÁÂÃÄÅ ÇĆČ ĐÈÉÊË ĞĢ Īİ ŁŃÑ ŐÖ ŘŠ ŤŰÜ ŴÝŸ Ž\nàáâãäå çćč đèéêë ğģ īı łńñ őö řš ťűü ŵýÿ ž'],['Diacritics · composed / decomposed','Ångström naïve façade piñata\nA\u030a e\u0301 o\u0308 n\u0303 c\u0327 a\u0301\u0323'],['Cyrillic · localization','БГДЛПТ бвгдпт Ѓѓ Ќќ\nЂђ Љљ Њњ Ћћ Џџ'],['Figures · fractions · ligatures','0123456789 1/2 3/4 11/16\noffice affine ffi ffl fi fl'],['Currencies','€ $ ¢ £ ¤ ¥ ₴ ₽ ₺ ₹'],['Math · punctuation','+ − × ÷ = ≠ ≤ ≥ ± ∞ ∑ ∏ √ ∫\n“Round.” ‘Warm.’ (Quiet) [Clear] {Goeist}'],['Code','const round = (r) => r >= 0.5;\nif (a != b && i++ <= 10) { return [0x1F, "ok"]; }']];
for(const [title,text] of scriptSamples){const card=document.createElement('div');card.className='script-card';const label=document.createElement('div');label.className='meta';label.textContent=title;const specimen=document.createElement('div');specimen.className='goeist needs-font supplemental';specimen.textContent=text;card.append(label,specimen);$('#scripts').append(card)}
for(const size of [12,14,16,20,24,32,48,72]){const row=document.createElement('div');row.className='water-row';const label=document.createElement('span');label.textContent=size;const text=document.createElement('span');text.className='water-text goeist needs-font';text.style.fontSize=size+'px';text.textContent='The quick brown fox jumps over the lazy dog. Hamburgefontsiv 0123456789';row.append(label,text);$('#waterfall').append(row)}
for(const item of manifest.atlases){const option=document.createElement('option');option.value=item.url;option.textContent=item.label;$('#atlas').append(option)}
for(const style of Object.keys(manifest.fonts).sort((a,b)=>(a==='italic')-(b==='italic'))){const option=document.createElement('option');option.value=style;option.textContent=style[0].toUpperCase()+style.slice(1);$('#style').append(option)}
$('#atlas').value=manifest.atlases.find(a=>a.default).url;
function selectedStyle(){return $('#style').value}
function covered(style,reference=false){return new Set(manifest.fonts[style][reference?'reference':'goeist'].cmap)}
function missingText(text,cmap){return [...new Set([...text].filter(c=>!['\n','\r','\t'].includes(c)&&!cmap.has(c.codePointAt(0))))]}
function cp(c){return 'U+'+c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')}
function renderCovered(node,text,cmap){node.replaceChildren();let run='';function flush(){if(run){node.append(document.createTextNode(run));run=''}}for(const character of text){if(cmap.has(character.codePointAt(0))||['\n','\r','\t'].includes(character)){run+=character}else{flush();const missing=document.createElement('span');missing.textContent='['+cp(character)+']';missing.title='Unsupported character, not a font glyph';missing.style.cssText='font:11px ui-monospace,monospace;color:#9b4618;letter-spacing:0';node.append(missing)}}flush()}
function update(){const style=selectedStyle(),fontStyle=style==='italic'?'italic':'normal',weight=$('#weight').value,size=$('#size').value,language=$('#language').value,text=$('#text').value;$('#weight-value').textContent=weight;$('#size-value').textContent=size+' px';const features=[...$('#features').querySelectorAll('input')].map(i=>`"${i.value}" ${i.checked?1:0}`).join(', ');
for(const node of document.querySelectorAll('.goeist,.geist')){node.style.fontStyle=fontStyle;node.style.fontWeight=manifest.axis.tag==='wght'?weight:'400';node.style.fontVariationSettings=`"${manifest.axis.tag}" ${weight}`;node.style.fontFeatureSettings=features;node.style.fontSynthesis='none';node.lang=language;node.classList.toggle('ready',state.loaded.has(style))}
for(const id of ['#rounded','#original']){renderCovered($(id),text,covered(style,id==='#original'));$(id).style.setProperty('--size',size+'px')}
const roundedMissing=missingText(text,covered(style)),originalMissing=missingText(text,covered(style,true));const warnings=[];if(roundedMissing.length)warnings.push('__FAMILY__ unsupported: '+roundedMissing.map(cp).join(' '));if(originalMissing.length)warnings.push('Original unsupported: '+originalMissing.map(cp).join(' '));$('#coverage').textContent=warnings.length?warnings.join(' · ')+'. Explicit codepoint labels replace missing characters; no fallback glyphs are displayed.':'Custom text is covered by both repertoires; font load status is shown above.';
for(const node of document.querySelectorAll('.supplemental')){node.dataset.originalText??=node.textContent;renderCovered(node,node.dataset.originalText,covered(style));node.title='Unsupported characters, if any, appear as explicit codepoint labels rather than fallback glyphs.'}
const loaded=state.loaded.has(style),failure=state.failures[style];$('#status').textContent=loaded?`Local ${style} __FAMILY__ WOFF2 and original __UPSTREAM__ TTF loaded. Font synthesis disabled.`:failure?`Font load failed for ${style}: ${failure}. Text proof is hidden.`:`Loading ${style} fonts…`;$('#status').dataset.state=loaded?'ready':failure?'error':'loading'}
async function loadFonts(){for(const [style,entry] of Object.entries(manifest.fonts)){try{for(const [kind,family] of [['goeist','GoeistProof'],['reference','GeistProof']]){const face=new FontFace(family,`url("${entry[kind].url}")`,{style:style==='italic'?'italic':'normal',weight:manifest.axis.tag==='wght'?`${manifest.axis.min} ${manifest.axis.max}`:'400',display:'block'});await face.load();document.fonts.add(face)}state.loaded.add(style);update()}catch(error){state.failures[style]=error.message;update();console.error(error)}}}
const ns='http://www.w3.org/2000/svg';
function renderAtlas(){if(!state.atlas)return;const query=$('#search').value.trim().toLowerCase().replace(/^u\+/,'');const matches=state.atlas.glyphs.filter(g=>!query||g.name.toLowerCase().includes(query)||g.codepoints.some(n=>n.toString(16).padStart(4,'0').includes(query)||String.fromCodePoint(n).toLowerCase()===query));$('#glyph-count').textContent=`${matches.length} / ${state.atlas.glyphs.length} glyphs`;$('#glyphs').replaceChildren();const upm=state.atlas.upm;for(const glyph of matches.slice(0,state.limit)){const cell=document.createElement('div');cell.className='glyph';const svg=document.createElementNS(ns,'svg');const top=Math.max(state.atlas.ascender,upm*.95),bottom=Math.min(state.atlas.descender,-upm*.25),width=Math.max(glyph.advance,upm*.85);svg.setAttribute('viewBox',`${-upm*.12} ${-top} ${width+upm*.24} ${top-bottom}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',glyph.name);const path=document.createElementNS(ns,'path');path.setAttribute('d',glyph.path);path.setAttribute('transform','scale(1,-1)');path.setAttribute('fill','currentColor');const baseline=document.createElementNS(ns,'path');baseline.setAttribute('d',`M ${-upm*.1} 0 H ${width+upm*.1}`);baseline.setAttribute('stroke','#d8ddd3');baseline.setAttribute('stroke-width','3');svg.append(baseline,path);const name=document.createElement('b');name.textContent=glyph.name;const unicode=document.createElement('small');unicode.textContent=glyph.codepoints.length?glyph.codepoints.map(n=>'U+'+n.toString(16).toUpperCase().padStart(4,'0')).join(' '):'Unencoded';const metrics=document.createElement('small');metrics.textContent=`Advance ${Math.round(glyph.advance*100)/100}`;cell.append(svg,name,unicode,metrics);$('#glyphs').append(cell)}$('#more').disabled=matches.length<=state.limit;$('#more').textContent=matches.length<=state.limit?'All shown':`Show ${Math.min(180,matches.length-state.limit)} more`}
function renderMetrics(){if(!state.atlas)return;const a=state.atlas,upm=a.upm,codes=[72,120,100,111,112],glyphs=codes.map(c=>a.glyphs.find(g=>g.codepoints.includes(c))).filter(Boolean);let x=0;const svg=document.createElementNS(ns,'svg'),width=glyphs.reduce((s,g)=>s+g.advance,0),top=a.ascender,bottom=a.descender;svg.setAttribute('viewBox',`${-upm*.6} ${-top-upm*.05} ${width+upm*.7} ${top-bottom+upm*.1}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','Vertical metrics');for(const [label,y] of Object.entries(a.metrics)){const line=document.createElementNS(ns,'path');line.setAttribute('d',`M ${-upm*.55} ${-y} H ${width+upm*.05}`);line.setAttribute('stroke','#356343');line.setAttribute('stroke-width','2');const text=document.createElementNS(ns,'text');text.setAttribute('x',-upm*.55);text.setAttribute('y',-y-10);text.setAttribute('font-size',upm*.045);text.setAttribute('fill','#356343');text.textContent=`${label} ${y}`;svg.append(line,text)}for(const g of glyphs){const p=document.createElementNS(ns,'path');p.setAttribute('d',g.path);p.setAttribute('transform',`translate(${x},0) scale(1,-1)`);p.setAttribute('fill','currentColor');const t=document.createElementNS(ns,'text');t.setAttribute('x',x+g.advance/2);t.setAttribute('y',-bottom+upm*.04);t.setAttribute('text-anchor','middle');t.setAttribute('font-size',upm*.035);t.setAttribute('fill','#696e67');t.textContent=Math.round(g.advance);svg.append(p,t);x+=g.advance}$('#metrics').replaceChildren(svg)}
const spacingLines=['nnnonnnoonnoonnn','HHHOHHHOOHHOOHHH','n'+'abcdefghijklmnopqrstuvwxyz'.split('').join('n')+'n','H'+'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').join('H')+'H','0102030405060708090'];
for(const line of spacingLines){const row=document.createElement('div');row.className='goeist needs-font spacing-line';row.textContent=line;$('#spacing').append(row)}
function renderCharset(){const style=selectedStyle(),cmap=manifest.fonts[style].goeist.cmap.filter(c=>c>32&&!(c>=0x7f&&c<0xa0));$('#charset').replaceChildren(...cmap.map(c=>{const s=document.createElement('span');s.textContent=String.fromCodePoint(c);s.title='U+'+c.toString(16).toUpperCase().padStart(4,'0');return s}));$('#charset-count').textContent=`${cmap.length} encoded characters in the ${style} variable font, set in the font itself`}
async function loadAtlas(){const request=++state.atlasRequest;$('#atlas-status').textContent='Loading complete outline atlas…';try{const response=await fetch($('#atlas').value);if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();if(request!==state.atlasRequest)return;state.atlas=data;state.limit=180;$('#atlas-status').textContent='';renderAtlas();renderMetrics()}catch(error){if(request!==state.atlasRequest)return;$('#atlas-status').textContent=`Atlas unavailable: ${error.message}. Serve the repository with HTTP, not file://.`}}
for(const id of ['#style','#weight','#size','#language','#text'])$(id).addEventListener('input',update);$('#style').addEventListener('input',renderCharset);$('#atlas').addEventListener('change',loadAtlas);$('#search').addEventListener('input',()=>{state.limit=180;renderAtlas()});$('#more').addEventListener('click',()=>{state.limit+=180;renderAtlas()});update();renderCharset();loadFonts();loadAtlas();
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", default="Goeist", choices=sorted(FAMILIES))
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
        parser.error("AUTHORS.txt must identify the Goeist author")
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
                manifest["fonts"][style] = {"goeist": {"url": relative_url(web, args.output),
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
    if set(variables) != set(family.slopes) or set(references) != set(family.slopes):
        parser.error(f"Variable fonts for {', '.join(family.slopes)} are required for {family.name} "
                     f"and original {family.upstream_label}")
    tag, low, default, high = family.axis
    statics = {(style.slope, style.name): style for style in family.styles}
    static_keys = set()
    for path in sorted((args.fonts / "ttf").glob("*.ttf")):
        with TTFont(path) as font:
            if "fvar" in font:
                continue
            name = path.stem.split("-", 1)[1]
            key = (style_of(font), name)
            if key not in statics or key in static_keys:
                parser.error(f"Unexpected or duplicate static style: {path.name}")
            static_keys.add(key)
            style = statics[key]
            label = name if family.element_shapes else style.weight
            filename = f"{style.slope}-{label}.json"
            (atlas_dir / filename).write_text(json.dumps(atlas(font), separators=(",", ":")))
            manifest["atlases"].append({"label": f"{style.slope.title()} · {label} · static TTF",
                                        "slope": style.slope,
                                        "order": family.styles.index(style) if family.element_shapes else style.weight,
                                        "default": style.slope == "upright" and dict(style.location)[tag] == default,
                                        "url": f"atlases/{filename}"})
    if static_keys != set(statics):
        parser.error(f"All {len(statics)} static styles are required; missing: {sorted(set(statics) - static_keys)}")
    # Weight interpolates outlines, so sample between masters; Element Shape only swaps glyphs.
    for slope, path in ({} if family.element_shapes else variables).items():
        with TTFont(path) as font:
            for weight in INTERMEDIATES:
                filename = f"{slope}-{weight}-variable.json"
                (atlas_dir / filename).write_text(json.dumps(atlas(font, {tag: weight}), separators=(",", ":")))
                manifest["atlases"].append({"label": f"{slope.title()} · {weight} · variable instance",
                                            "slope": slope, "order": weight, "default": False,
                                            "url": f"atlases/{filename}"})
    manifest["atlases"].sort(key=lambda a: (a["slope"] == "italic", a["order"]))
    manifest["axis"] = {"tag": tag, "min": low, "max": high, "default": default}
    if family.element_shapes:
        replacements = {
            "__INTRO__": "Explore every Element Shape dot, every stylistic set, and the complete exported glyph repertoire.",
            "__BADGE__": "Regular · Round, Square, Triangle and Heart dots",
            "__AXIS_LABEL__": "Element shape", "__AXIS_STEP__": "25",
            "__ATLAS_NOTE__": "Atlases cover the four static shapes: Regular, Square, Triangle and Heart.",
        }
    else:
        replacements = {
            "__INTRO__": "Explore nine weights, genuine italics, every stylistic set, and the complete exported glyph repertoire.",
            "__BADGE__": f"{low} — {high} · Upright + Italic",
            "__AXIS_LABEL__": "Weight", "__AXIS_STEP__": "1",
            "__ATLAS_NOTE__": "Atlases cover all nine static weights in each style and variable instances at 250, 550 and 850.",
        }
    replacements.update({"__AXIS_MIN__": str(low), "__AXIS_MAX__": str(high), "__AXIS_DEFAULT__": str(default),
                         "__AUTHOR__": author, "__FAMILY__": family.name, "__UPSTREAM__": family.upstream_label})
    page = PAGE.replace("__MANIFEST__", json.dumps(manifest, ensure_ascii=True).replace("<", "\\u003c"))
    for placeholder, value in replacements.items():
        page = page.replace(placeholder, html.escape(value))
    (args.output / "index.html").write_text(page)
    print(f"Generated {args.output / 'index.html'} and {len(manifest['atlases'])} full-glyph atlases.")
    print("Serve the repository root with HTTP, then open /" + relative_url(args.output, Path.cwd()) + "/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
