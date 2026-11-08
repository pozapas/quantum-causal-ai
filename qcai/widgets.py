"""Client-side widgets for the static book: the learning map and the placement dialog.

Both return IPython HTML with inline CSS and JavaScript.  They need no kernel and
no external library, so they work on GitHub Pages.  Data comes from the reviewed
lesson files in _data/levels/.
"""
from __future__ import annotations

import json
import pathlib
import uuid

from IPython.display import HTML

ROOT = pathlib.Path(__file__).resolve().parents[1]
STAGES = ["Grades 1-3", "Grades 4-6", "Grades 7-9", "High-school bridge", "Undergraduate",
          "Advanced undergraduate", "Graduate", "Doctoral and postdoctoral"]
SHORT = ["Notice and count", "Chance and waves", "Evidence and graphs", "Math toolkit",
         "Classical causal AI", "Quantum information", "Quantum causal models", "Research frontier"]
COLORS = ["#8b5cf6", "#7c3aed", "#6d28d9", "#4f46e5", "#2563eb", "#0284c7", "#0891b2", "#0d9488"]


def _levels():
    return [json.loads((ROOT / "_data" / "levels" / f"level{n}.json").read_text(encoding="utf-8")) for n in range(8)]


def _icon(name: str) -> str:
    svg = (ROOT / "_static" / "icons" / f"qicon-{name}.svg").read_text(encoding="utf-8")
    # make gradient ids unique per inline copy so several icons can share a page
    tag = uuid.uuid4().hex[:6]
    return svg.replace(f"-{name}", f"-{name}-{tag}").replace('width="48" height="48"', 'width="100%" height="100%"')


# ---------------------------------------------------------------------------
# Learning map
# ---------------------------------------------------------------------------

MAP_CSS = """
.qw{--bg:#fff;--ink:#1e1b4b;--muted:#64748b;--line:#cbd5e1;--card:#f8fafc;--pre:#7c3aed;--post:#0891b2;font-family:Inter,"Segoe UI",system-ui,sans-serif;color:var(--ink)}
html.dark .qw{--bg:#0b1020;--ink:#e2e8f0;--muted:#94a3b8;--line:#334155;--card:#111827;--pre:#a78bfa;--post:#22d3ee}
.qw *{box-sizing:border-box}
.qw-bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.25rem 0 .75rem}
.qw-chip{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:.3rem .7rem;font-size:.8rem;cursor:pointer;display:inline-flex;align-items:center;gap:.35rem}
.qw-chip[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.qw-chip i{width:.6rem;height:.6rem;border-radius:50%;display:inline-block}
.qw-search{flex:1 1 12rem;min-width:10rem;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:.6rem;padding:.4rem .7rem;font-size:.85rem}
.qw-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:1rem;background:var(--card)}
.qw-scroll:focus{outline:2px solid var(--pre);outline-offset:2px}
.qw .qw-scroll>svg{display:block;min-width:560px;width:100%;height:auto}
.qw .edge{fill:none;stroke:var(--line);stroke-width:1.2;opacity:.55;transition:opacity .2s,stroke .2s,stroke-width .2s}
.qw .edge.pre{stroke:var(--pre);opacity:1;stroke-width:2.2}
.qw .edge.post{stroke:var(--post);opacity:1;stroke-width:2.2}
.qw .node{cursor:pointer;transition:opacity .2s}
.qw .node circle{fill:var(--bg);stroke-width:2.4;transition:r .15s}
.qw .node text{font-size:10.5px;font-weight:700;fill:var(--ink);text-anchor:middle;dominant-baseline:central;pointer-events:none}
.qw .node:focus{outline:none}.qw .node:focus circle,.qw .node:hover circle{r:16}
.qw .node.sel circle{stroke-width:4}.qw svg.wide .node text{font-size:12.5px}.qw svg.wide .node:hover circle,.qw svg.wide .node:focus circle{r:19}.qw svg.wide .rowlab{font-size:12.5px}.qw .colname{font-size:11.5px;font-weight:600;fill:var(--ink)}.qw svg.wide .rowsub{font-size:9.5px}
.qw .node.pre circle{fill:var(--pre)}.qw .node.post circle{fill:var(--post)}
.qw .node.pre text,.qw .node.post text{fill:#fff}
.qw.focus .node:not(.sel):not(.pre):not(.post){opacity:.18}.qw.focus .edge:not(.pre):not(.post){opacity:.08}
.qw .node.miss{opacity:.15}
.qw .rowlab{font-size:12.5px;font-weight:700;fill:var(--ink)}.qw .rowsub{font-size:10.5px;font-weight:500;fill:var(--muted)}
.qw .band{fill:var(--bg);opacity:.6}
.qw-panel{margin-top:.75rem;border:1px solid var(--line);border-radius:1rem;padding:.9rem 1.1rem;background:var(--card);min-height:5.5rem}
.qw-panel h4{margin:0 0 .25rem;font-size:1rem}.qw-panel p{margin:.2rem 0;font-size:.9rem;color:var(--muted)}
.qw-panel a.go{display:inline-block;margin-top:.4rem;font-weight:700;color:var(--pre)}
.qw-legend{display:flex;gap:1rem;flex-wrap:wrap;font-size:.78rem;color:var(--muted);margin-top:.5rem}
.qw-legend b{display:inline-block;width:1.4rem;height:.25rem;border-radius:2px;vertical-align:middle;margin-right:.35rem}
.qw-x{margin-left:auto;display:inline-flex;align-items:center;gap:.4rem;border:0;border-radius:.7rem;padding:.4rem .8rem;font-weight:700;font-size:.82rem;cursor:pointer;color:#fff;background:linear-gradient(135deg,#7c3aed,#06b6d4)}
.qw-x[hidden]{display:none}.qw .qw-x svg{width:1rem;height:1rem;min-width:0}
.qw-full{position:fixed;inset:0;z-index:1000;background:var(--bg);display:flex;flex-direction:column;padding:12px 16px 14px;gap:10px}
.qw-full .qw-slot .qw-bar{margin:0}.qw-full .qw-top{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem}
.qw-full .qw-top h3{margin:0 auto 0 0;font-size:1.05rem;color:var(--ink)}
.qw-tool{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:.6rem;min-width:2.2rem;height:2.2rem;padding:0 .6rem;font-weight:700;cursor:pointer}
.qw-tool:focus-visible,.qw-x:focus-visible{outline:3px solid var(--post);outline-offset:2px}
.qw-full .qw-stage{flex:1;min-height:0;display:grid;grid-template-columns:1fr 320px;gap:12px}
.qw-full .qw-scroll{overflow:hidden;cursor:grab;touch-action:none;height:100%}
.qw-full .qw-scroll.drag{cursor:grabbing}
.qw-full .qw-scroll>svg{min-width:0;width:100%;height:100%}
.qw-full .qw-panel{margin:0;overflow:auto}
.qw-hint{font-size:.78rem;color:var(--muted)}
@media (max-width:820px){.qw-full .qw-stage{grid-template-columns:1fr;grid-template-rows:1fr auto}.qw-full .qw-panel{max-height:34vh}}
@media (prefers-reduced-motion:no-preference){.qw .edge{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:qwdraw 1.2s ease forwards}
@keyframes qwdraw{to{stroke-dashoffset:0}}}
"""

MAP_JS = r"""
(function(){
const root=document.getElementById("__ID__"); if(!root||root.dataset.ready) return; root.dataset.ready="1";
const D=__DATA__, svgNS="http://www.w3.org/2000/svg";
const mk=(t,a={})=>{const e=document.createElementNS(svgNS,t);for(const k in a)e.setAttribute(k,a[k]);return e};
const svg=mk("svg",{role:"img","aria-label":"Prerequisite map of 80 lessons in 8 levels",preserveAspectRatio:"xMidYMid meet"});
const gB=mk("g"), gE=mk("g"), gN=mk("g"); svg.append(gB,gE,gN);
let W=640,H=654,mode="portrait",pos={},edges=[],vb=[0,0,W,H];
const byId=Object.fromEntries(D.nodes.map(n=>[n.id,n])), kids={};D.nodes.forEach(n=>n.pre.forEach(p=>(kids[p]=kids[p]||[]).push(n.id)));
const els={};
D.nodes.forEach(n=>{const g=mk("g",{class:"node",tabindex:"0",role:"button","aria-label":`${n.id}: ${n.title}`});g.dataset.node=n.id;
  const c=mk("circle",{r:13,stroke:D.colors[n.level]}), t=mk("text"), tt=mk("title");t.textContent=n.id.slice(3);tt.textContent=`${n.id} · ${n.title}`;
  g.append(tt,c,t);gN.append(g);els[n.id]={g,c,t};
  g.addEventListener("mouseenter",()=>{if(!pinned)show(n.id)});g.addEventListener("focus",()=>{if(!pinned)show(n.id)});
  g.addEventListener("click",()=>pin(n.id));g.addEventListener("keydown",ev=>{if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();pin(n.id)}});});
function wrap(s,n){if(s.length<=n)return [s];const sp=[...s.matchAll(/ /g)].map(m=>m.index);if(!sp.length)return [s];
  const c=sp.reduce((b,i)=>Math.abs(i-s.length/2)<Math.abs(b-s.length/2)?i:b,sp[0]);return [s.slice(0,c),s.slice(c+1)]}
function setVB(){svg.setAttribute("viewBox",vb.map(v=>v.toFixed(1)).join(" "))}
function layout(m){mode=m;svg.classList.toggle("wide",m!=="portrait");gB.replaceChildren();gE.replaceChildren();edges=[];
  if(m==="portrait"){const pad=12,top=8,rowH=80,colW=(640-2*pad)/10;W=640;H=top+rowH*8+6;
    D.nodes.forEach(n=>{pos[n.id]=[pad+colW*(n.i+.5),top+rowH*n.level+50]});
    D.levels.forEach((L,k)=>{const y=top+rowH*k;if(k%2===0)gB.append(mk("rect",{x:0,y,width:W,height:rowH,class:"band"}));
      const t=mk("text",{x:pad+14,y:y+17,class:"rowlab"});t.innerHTML=`Level ${k} · ${L.short}<tspan class="rowsub" dx="8">${L.stage}</tspan>`;gB.append(t);
      gB.append(mk("circle",{cx:pad+5,cy:y+13,r:4,fill:D.colors[k]}))});}
  else{const left=14,top=100,colW=136,rowH=52;W=left*2+colW*8;H=top+rowH*10+8;
    D.nodes.forEach(n=>{pos[n.id]=[left+colW*(n.level+.5),top+rowH*(n.i+.5)]});
    D.levels.forEach((L,k)=>{const x=left+colW*k;if(k%2===0)gB.append(mk("rect",{x,y:0,width:colW,height:H,class:"band"}));
      gB.append(mk("rect",{x:x+colW/2-22,y:10,width:44,height:5,rx:2.5,fill:D.colors[k]}));
      const a=mk("text",{x:x+colW/2,y:31,class:"rowlab","text-anchor":"middle"});a.textContent=`Level ${k}`;gB.append(a);
      wrap(L.short,14).forEach((ln,i)=>{const t=mk("text",{x:x+colW/2,y:47+i*14,class:"colname","text-anchor":"middle"});t.textContent=ln;gB.append(t)});
      const b=mk("text",{x:x+colW/2,y:82,class:"rowsub","text-anchor":"middle"});b.textContent=L.stage;gB.append(b)});}
  D.nodes.forEach(n=>n.pre.forEach(p=>{const [x1,y1]=pos[p],[x2,y2]=pos[n.id];let d;
    if(m==="portrait"){ if(Math.abs(y1-y2)<1){const mx=(x1+x2)/2;d=`M${x1},${y1+14} Q${mx},${y1+14+Math.min(24,4+Math.abs(x2-x1)/5)} ${x2},${y2+14}`}
      else{const my=(y1+y2)/2;d=`M${x1},${y1+15} C${x1},${my} ${x2},${my} ${x2},${y2-15}`}}
    else{ if(Math.abs(x1-x2)<1){const my=(y1+y2)/2;d=`M${x1+17},${y1} Q${x1+17+Math.min(40,8+Math.abs(y2-y1)/5)},${my} ${x2+17},${y2}`}
      else{const mx=(x1+x2)/2;d=`M${x1+17},${y1} C${mx},${y1} ${mx},${y2} ${x2-17},${y2}`}}
    const e=mk("path",{d,class:"edge"});gE.append(e);edges.push({from:p,to:n.id,el:e});}));
  edges.forEach(e=>{const l=Math.ceil(e.el.getTotalLength?e.el.getTotalLength():400);e.el.style.setProperty("--len",l)});
  D.nodes.forEach(n=>{const [x,y]=pos[n.id],E=els[n.id];E.c.setAttribute("r",m==="portrait"?13:16);E.c.setAttribute("cx",x);E.c.setAttribute("cy",y);E.t.setAttribute("x",x);E.t.setAttribute("y",y)});
  vb=[0,0,W,H];setVB();if(pinned)show(pinned)}
svg.addEventListener("mouseleave",()=>{if(!pinned)clear()});
function walk(id,next){const seen=new Set(),st=[id];while(st.length){const u=st.pop();(next(u)||[]).forEach(v=>{if(!seen.has(v)){seen.add(v);st.push(v)}})}return seen}
const panel=root.querySelector(".qw-panel");let pinned=null;
function clear(){root.classList.remove("focus");Object.values(els).forEach(E=>E.g.classList.remove("pre","post","sel"));edges.forEach(e=>e.el.classList.remove("pre","post"));
  panel.innerHTML=`<h4>Hover, tap, or tab to a lesson</h4><p>Violet shows everything that lesson builds on. Cyan shows everything it unlocks. Click to pin a lesson.</p>`}
function show(id){const n=byId[id],A=walk(id,u=>byId[u].pre),B=walk(id,u=>kids[u]);root.classList.add("focus");
  Object.entries(els).forEach(([k,E])=>{E.g.classList.toggle("sel",k===id);E.g.classList.toggle("pre",A.has(k));E.g.classList.toggle("post",B.has(k))});
  edges.forEach(e=>{e.el.classList.toggle("pre",A.has(e.from)&&(A.has(e.to)||e.to===id));e.el.classList.toggle("post",B.has(e.to)&&(B.has(e.from)||e.from===id))});
  const pre=n.pre.length?n.pre.join(", "):"none";
  panel.innerHTML=`<h4>${n.id} · ${n.title}</h4><p>${n.objective}</p><p>Builds directly on: ${pre}. All earlier steps: ${A.size}. Lessons it unlocks: ${B.size}.</p><a class="go" href="${D.base}levels/level-${n.level}/${n.id.toLowerCase()}/">Open ${n.id} →</a>`}
function pin(id){if(pinned===id){pinned=null;clear();return}pinned=id;show(id)}
const scroll=root.querySelector(".qw-scroll");scroll.append(svg);layout("portrait");clear();
const chips=root.querySelectorAll(".qw-chip");chips.forEach(ch=>ch.addEventListener("click",()=>{chips.forEach(c=>c.setAttribute("aria-pressed","false"));ch.setAttribute("aria-pressed","true");
  const L=ch.dataset.level;Object.entries(els).forEach(([k,E])=>E.g.classList.toggle("miss",L!=="all"&&String(byId[k].level)!==L))}));
root.querySelector(".qw-search").addEventListener("input",ev=>{const q=ev.target.value.trim().toLowerCase();
  Object.entries(els).forEach(([k,E])=>{const n=byId[k];E.g.classList.toggle("miss",!!q&&!(n.id.toLowerCase().includes(q)||n.title.toLowerCase().includes(q)||n.objective.toLowerCase().includes(q)))})});
// ---- full-screen viewer: wide layout, zoom and pan ----
const bar=root.querySelector(".qw-bar"), legend=root.querySelector(".qw-legend"), xbtn=root.querySelector(".qw-x");
let full=null, back=null, drag=null;
function zoom(f,cx,cy){const nw=Math.min(W*1.2,Math.max(W/8,vb[2]*f)), nh=nw*H/W;
  if(cx===undefined){cx=vb[0]+vb[2]/2;cy=vb[1]+vb[3]/2}
  vb=[cx-(cx-vb[0])*nw/vb[2], cy-(cy-vb[1])*nh/vb[3], nw, nh]; setVB()}
function fit(){vb=[0,0,W,H];setVB()}
function toSvg(e){const r=svg.getBoundingClientRect(), s=Math.max(vb[2]/r.width,vb[3]/r.height);
  const ox=r.left+(r.width-vb[2]/s)/2, oy=r.top+(r.height-vb[3]/s)/2; return [vb[0]+(e.clientX-ox)*s, vb[1]+(e.clientY-oy)*s, s]}
function onWheel(e){e.preventDefault();const [x,y]=toSvg(e);zoom(e.deltaY>0?1.15:1/1.15,x,y)}
function down(e){if(e.target.closest&&e.target.closest("g.node"))return;drag={x:e.clientX,y:e.clientY,vb:vb.slice()};scroll.classList.add("drag");scroll.setPointerCapture(e.pointerId)}
function move(e){if(!drag)return;const s=toSvg(e)[2];vb=[drag.vb[0]-(e.clientX-drag.x)*s, drag.vb[1]-(e.clientY-drag.y)*s, vb[2], vb[3]];setVB()}
function up(){drag=null;scroll.classList.remove("drag")}
function key(e){if(!full)return;const inInput=e.target.matches&&e.target.matches("input");
  if(e.key==="Escape"){e.preventDefault();close()}
  else if(!inInput&&(e.key==="+"||e.key==="=")){zoom(1/1.25)}else if(!inInput&&e.key==="-"){zoom(1.25)}else if(!inInput&&e.key==="0"){fit()}
  else if(e.key==="Tab"){const f=[...full.querySelectorAll("button,input,a[href],g.node:not(.miss)")];const a=f[0],z=f[f.length-1];
    if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}}
function open(){if(full)return;back=document.activeElement;full=document.createElement("div");full.className="qw-full";
  full.setAttribute("role","dialog");full.setAttribute("aria-modal","true");full.setAttribute("aria-label","Learning map, full screen");
  full.innerHTML=`<div class="qw-top"><h3>Learning map</h3><span class="qw-hint">Scroll or press + and − to zoom, drag to move, Esc to close</span>
   <button type="button" class="qw-tool" data-z="in" aria-label="Zoom in">+</button><button type="button" class="qw-tool" data-z="out" aria-label="Zoom out">−</button>
   <button type="button" class="qw-tool" data-z="fit">Fit</button><button type="button" class="qw-tool" data-z="close">Close</button></div>
   <div class="qw-slot"></div><div class="qw-stage"></div>`;
  root.append(full);document.documentElement.style.overflow="hidden";xbtn.hidden=true;
  full.querySelector(".qw-slot").append(bar);full.querySelector(".qw-stage").append(scroll,panel);
  layout("landscape");
  scroll.addEventListener("wheel",onWheel,{passive:false});scroll.addEventListener("pointerdown",down);
  scroll.addEventListener("pointermove",move);scroll.addEventListener("pointerup",up);scroll.addEventListener("pointercancel",up);
  full.querySelector("[data-z=in]").onclick=()=>zoom(1/1.25);full.querySelector("[data-z=out]").onclick=()=>zoom(1.25);
  full.querySelector("[data-z=fit]").onclick=fit;full.querySelector("[data-z=close]").onclick=close;
  document.addEventListener("keydown",key);full.querySelector("[data-z=close]").focus()}
function close(){if(!full)return;scroll.removeEventListener("wheel",onWheel);scroll.removeEventListener("pointerdown",down);
  scroll.removeEventListener("pointermove",move);scroll.removeEventListener("pointerup",up);scroll.removeEventListener("pointercancel",up);
  document.removeEventListener("keydown",key);
  root.prepend(bar);bar.after(scroll);legend.after(panel);xbtn.hidden=false;layout("portrait");
  full.remove();full=null;document.documentElement.style.overflow="";(back&&back.isConnected?back:xbtn).focus()}
xbtn.addEventListener("click",open);
})();
"""


def learning_map(base: str = "../../") -> HTML:
    """Interactive prerequisite map of every lesson.  `base` climbs from the page to the book root."""
    lv = _levels()
    nodes = [{"id": L["id"], "level": l["level"], "i": i, "title": L["title"], "objective": L["objective"],
              "pre": L["prerequisites"]} for l in lv for i, L in enumerate(l["lessons"])]
    data = {"nodes": nodes, "colors": COLORS, "base": base,
            "levels": [{"short": SHORT[l["level"]], "stage": STAGES[l["level"]]} for l in lv]}
    wid = "qmap-" + uuid.uuid4().hex[:8]
    chips = '<button type="button" class="qw-chip" data-level="all" aria-pressed="true">All levels</button>' + "".join(
        f'<button type="button" class="qw-chip" data-level="{k}" aria-pressed="false"><i style="background:{COLORS[k]}"></i>Level {k}</button>'
        for k in range(8))
    html = f"""<style>{MAP_CSS}</style>
<div class="qw" id="{wid}" data-qcai-widget="map">
  <div class="qw-bar">{chips}<input class="qw-search" type="search" placeholder="Search lessons, e.g. Bayes or qubit" aria-label="Search lessons"><button type="button" class="qw-x" data-act="expand" aria-label="Expand the learning map to full screen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>Expand</button></div>
  <div class="qw-scroll" tabindex="0" role="region" aria-label="Learning map, scroll sideways on small screens"></div>
  <div class="qw-legend"><span><b style="background:var(--pre)"></b>builds on (all earlier steps)</span><span><b style="background:var(--post)"></b>unlocks (all later steps)</span><span>Rows are levels; numbers are lesson numbers within a level.</span></div>
  <div class="qw-panel" aria-live="polite"></div>
</div>
<script>{MAP_JS.replace("__ID__", wid).replace("__DATA__", json.dumps(data, ensure_ascii=False))}</script>"""
    return HTML(html)


# ---------------------------------------------------------------------------
# Placement dialog
# ---------------------------------------------------------------------------

QUESTIONS = [
    # (rung level if missed, prompt, options, index of correct option)
    (0, "You flip a fair coin two times. What is the chance of getting two heads?", ["1/2", "1/4", "1/3"], 1),
    (1, "Solve for x:  3x + 2 = 11", ["x = 3", "x = 4", "x = 13/3"], 0),
    (2, "Ice-cream sales and swimming accidents rise and fall together over a year. What is the most likely explanation?",
     ["Ice cream causes accidents", "Accidents cause ice-cream sales", "Hot weather drives both"], 2),
    (3, "The matrix [[0, 1], [1, 0]] multiplies the column vector (1, 0). What is the result?",
     ["(1, 0)", "(0, 1)", "(1, 1)"], 1),
    (4, "A treatment X and an outcome Y share one measured common cause Z, and nothing else confounds them. "
        "To estimate the effect of X on Y from observational data, you should:",
     ["Adjust for Z", "Adjust for a variable that both X and Y cause", "Ignore Z, because it is neither X nor Y"], 0),
    (5, "A qubit is in the state (|0⟩ + |1⟩)/√2. You measure it in the 0/1 basis. What is the chance of reading 0?",
     ["1/√2", "1", "1/2"], 2),
    (6, "In the quantum switch, what is placed in superposition?",
     ["Two copies of the same state", "The order in which two operations act", "The result of a measurement"], 1),
]

PLACE_CSS = """
.qp{--bg:#ffffff;--ink:#1e1b4b;--muted:#64748b;--line:#e2e8f0;--soft:#f5f3ff;--acc:#7c3aed;--acc2:#06b6d4;font-family:Inter,"Segoe UI",system-ui,sans-serif}
html.dark .qp{--bg:#0f172a;--ink:#e2e8f0;--muted:#94a3b8;--line:#1e293b;--soft:#1e1b4b;--acc:#a78bfa;--acc2:#22d3ee}
.qp *{box-sizing:border-box}
.qp-cta{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;border:1px solid var(--line);border-radius:1.1rem;padding:1rem 1.2rem;background:linear-gradient(135deg,rgba(124,58,237,.08),rgba(6,182,212,.08))}
.qp-cta .ic{width:52px;height:52px;flex:none}
.qp-cta p{margin:0;color:var(--ink)}.qp-cta small{color:var(--muted)}
.qp-btn{border:0;border-radius:.8rem;padding:.65rem 1.1rem;font-weight:700;font-size:.95rem;cursor:pointer;background:linear-gradient(135deg,#7c3aed,#06b6d4);color:#fff}
.qp-btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.qp-btn:focus-visible,.qp-opt:focus-visible{outline:3px solid var(--acc2);outline-offset:2px}
.qp-veil{position:fixed;inset:0;background:rgba(15,10,46,.55);backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;z-index:1000;padding:16px}
.qp-veil.open{display:flex}
.qp-dlg{width:min(560px,100%);max-height:calc(100vh - 32px);overflow:auto;background:var(--bg);color:var(--ink);border-radius:1.4rem;box-shadow:0 30px 80px -20px rgba(49,46,129,.6);position:relative}
.qp-head{position:relative;height:150px;border-radius:1.4rem 1.4rem 0 0;overflow:hidden;background:radial-gradient(500px 200px at 20% 0%,rgba(124,58,237,.65),transparent 60%),radial-gradient(400px 220px at 100% 100%,rgba(6,182,212,.6),transparent 60%),#0f0a2e}
.qp-head svg{position:absolute;inset:0;width:100%;height:100%}
.qp-body{padding:1.3rem 1.5rem 1.5rem}
.qp-body h2{margin:.1rem 0 .4rem;font-size:1.35rem;line-height:1.25;color:var(--ink);border:0}
.qp-body p{margin:.3rem 0 .8rem;color:var(--muted);font-size:.95rem}
.qp-x{position:absolute;top:.6rem;right:.6rem;width:2.2rem;height:2.2rem;border-radius:50%;border:0;background:rgba(255,255,255,.18);color:#fff;font-size:1.2rem;cursor:pointer;z-index:2}
.qp-prog{height:5px;border-radius:999px;background:var(--line);overflow:hidden;margin:.2rem 0 1rem}.qp-prog i{display:block;height:100%;background:linear-gradient(90deg,#7c3aed,#06b6d4);transition:width .35s}
.qp-opt{display:block;width:100%;text-align:left;margin:.45rem 0;padding:.75rem .95rem;border-radius:.85rem;border:1px solid var(--line);background:var(--bg);color:var(--ink);font-size:.95rem;cursor:pointer;transition:border-color .15s,transform .15s}
.qp-opt:hover{border-color:var(--acc);transform:translateX(2px)}
.qp-row{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1rem}
.qp-res{display:flex;gap:1rem;align-items:center;margin:.2rem 0 .6rem}.qp-res .ic{width:64px;height:64px;flex:none}
.qp-tag{display:inline-block;font-size:.75rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--acc)}
.qp-chip{display:none;margin-top:.6rem;font-size:.85rem;color:var(--muted)}.qp-chip a{font-weight:700}
@media (prefers-reduced-motion:no-preference){.qp-dlg{animation:qpin .35s cubic-bezier(.2,.8,.2,1)}@keyframes qpin{from{opacity:0;transform:translateY(14px) scale(.98)}}
.qp-orbit{animation:qpspin 9s linear infinite;transform-origin:280px 75px}.qp-orbit2{animation:qpspin 14s linear infinite reverse;transform-origin:280px 75px}
@keyframes qpspin{to{transform:rotate(360deg)}}.qp-pulse{animation:qppulse 2.4s ease-in-out infinite}@keyframes qppulse{50%{opacity:.35}}
.qp-flow{stroke-dasharray:6 8;animation:qpflow 1.6s linear infinite}@keyframes qpflow{to{stroke-dashoffset:-28}}}
"""

DEFAULT_MOTION = """<svg viewBox="0 0 560 150" aria-hidden="true">
<g fill="none" stroke-linecap="round">
 <g class="qp-orbit"><ellipse cx="280" cy="75" rx="120" ry="34" stroke="rgba(165,243,252,.45)" stroke-width="1.5"/><circle cx="400" cy="75" r="5" fill="#a5f3fc"/></g>
 <g class="qp-orbit2"><ellipse cx="280" cy="75" rx="120" ry="34" transform="rotate(60 280 75)" stroke="rgba(196,181,253,.45)" stroke-width="1.5"/><circle cx="340" cy="-29" r="4" fill="#c4b5fd" transform="rotate(60 280 75)"/></g>
 <circle cx="280" cy="75" r="11" fill="url(#qpg)"/>
 <path class="qp-flow" d="M60 110 C110 60 150 60 190 80" stroke="#c4b5fd" stroke-width="2"/>
 <path class="qp-flow" d="M370 80 C410 55 460 60 505 40" stroke="#67e8f9" stroke-width="2"/>
 <circle class="qp-pulse" cx="60" cy="110" r="7" fill="#8b5cf6"/><circle cx="505" cy="40" r="7" fill="#06b6d4" class="qp-pulse"/>
</g>
<defs><radialGradient id="qpg"><stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="#a5f3fc"/><stop offset="1" stop-color="#7c3aed"/></radialGradient></defs>
</svg>"""

PLACE_JS = r"""
(function(){
const root=document.getElementById("__ID__"); if(!root||root.dataset.ready) return; root.dataset.ready="1";
const D=__DATA__, veil=root.querySelector(".qp-veil"), body=root.querySelector(".qp-body"), dlg=root.querySelector(".qp-dlg");
const KEY="qcai-placement-v1"; let last=null, step=0;
const store={get(){try{return JSON.parse(localStorage.getItem(KEY)||"null")}catch(e){return null}},set(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}};
function open(){last=document.activeElement;veil.classList.add("open");intro();setTimeout(()=>{const b=dlg.querySelector("button.qp-btn,button.qp-opt");b&&b.focus()},60)}
function close(){veil.classList.remove("open");const s=store.get()||{};s.seen=true;store.set(s);chip();last&&last.focus&&last.focus()}
function prog(p){return `<div class="qp-prog" aria-hidden="true"><i style="width:${p}%"></i></div>`}
function intro(){step=0;body.innerHTML=`<span class="qp-tag">Welcome</span><h2 id="__ID__-t">Find your starting point</h2>
<p>Answer up to seven short questions. Each one checks a skill the next level needs, and the check stops at the first one you skip or miss. It takes about a minute, and nothing leaves your browser.</p>
<p>Who is reading?</p>
${D.who.map((w,i)=>`<button type="button" class="qp-opt" data-who="${i}">${w}</button>`).join("")}
<div class="qp-row"><button type="button" class="qp-btn ghost" data-act="skip">Skip, I'll browse</button></div>`;
 body.querySelectorAll("[data-who]").forEach(b=>b.onclick=()=>{if(b.dataset.who==="0")result(0,"A grown-up reading along is the right way to start. Level 0 uses objects, light, and fair tests.");else ask(0)});
 body.querySelector("[data-act=skip]").onclick=close}
function ask(i){step=i;const q=D.q[i];body.innerHTML=`<span class="qp-tag">Question ${i+1} of ${D.q.length}</span>${prog(100*i/D.q.length)}
<h2 id="__ID__-t">${q.p}</h2>${q.o.map((o,k)=>`<button type="button" class="qp-opt" data-k="${k}">${o}</button>`).join("")}
<button type="button" class="qp-opt" data-k="-1">Not sure yet</button>`;
 body.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{const k=+b.dataset.k;
  if(k===q.a){ if(i+1<D.q.length) ask(i+1); else result(7,"You answered every check. Level 7 connects the research threads, and earlier levels stay open for review."); }
  else result(q.r, k<0?"You chose to stop here, which is a good place to start.":`That question checks a skill from Level ${q.r}. The correct answer was: ${q.o[q.a]}.`)});
 const f=body.querySelector(".qp-opt");f&&f.focus()}
function result(L,why){const lv=D.levels[L];store.set({level:L,seen:true,at:Date.now()});
 body.innerHTML=`<span class="qp-tag">Your starting point</span>${prog(100)}
<div class="qp-res"><div class="ic">${D.icons[L]}</div><div><h2 id="__ID__-t">Level ${L} · ${lv.title}</h2><p style="margin:0">${lv.stage}</p></div></div>
<p>${why}</p><p>${lv.intro}</p><p>If the first exercises feel easy, skim them and move on. Every page stays open, so you can jump ahead or back at any time.</p>
<div class="qp-row"><a class="qp-btn" style="text-decoration:none" href="${D.base}levels/level-${L}/">Start Level ${L}</a>
<a class="qp-btn ghost" style="text-decoration:none" href="${D.base}start/roadmap/">See the learning map</a>
<button type="button" class="qp-btn ghost" data-act="again">Retake</button></div>`;
 body.querySelector("[data-act=again]").onclick=intro;chip();body.querySelector("a.qp-btn").focus()}
function chip(){const s=store.get(),c=root.querySelector(".qp-chip");if(s&&s.level!=null){c.style.display="block";c.innerHTML=`Your saved starting point: <a href="${D.base}levels/level-${s.level}/">Level ${s.level} · ${D.levels[s.level].title}</a>`}}
root.querySelector("[data-act=open]").onclick=open;root.querySelector(".qp-x").onclick=close;
veil.addEventListener("click",e=>{if(e.target===veil)close()});
document.addEventListener("keydown",e=>{if(!veil.classList.contains("open"))return;if(e.key==="Escape")close();
 if(e.key==="Tab"){const f=[...dlg.querySelectorAll("button,a[href]")];if(!f.length)return;const a=f[0],z=f[f.length-1];
  if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}});
chip();const s=store.get();
if(location.hash==="#find-my-level"||!(s&&s.seen)){setTimeout(open,700)}
window.addEventListener("hashchange",()=>{if(location.hash==="#find-my-level")open()});
})();
"""


def placement(base: str = "./") -> HTML:
    """Call-to-action card plus a first-visit placement dialog (adaptive, client-side)."""
    lv = _levels()
    motion_file = ROOT / "_static" / "motion" / "intro.svg"
    motion = DEFAULT_MOTION
    if motion_file.exists():
        txt = motion_file.read_text(encoding="utf-8")
        # accept only a self-contained SVG: no scripts, event handlers or external references
        bad = ("<script", "javascript:", " onload=", " onclick=", "href=\"http", "xlink:href=\"http", "@import")
        if txt.lstrip().startswith("<svg") and not any(b in txt.lower() for b in bad) and len(txt) < 150_000:
            motion = txt
    data = {
        "base": base,
        "who": ["A young learner, with a grown-up reading along", "A student (middle school to university)",
                "A teacher or parent", "A researcher or working professional"],
        "q": [{"r": r, "p": p, "o": o, "a": a} for r, p, o, a in QUESTIONS],
        "levels": [{"title": l["title"], "stage": STAGES[l["level"]], "intro": l["intro"]} for l in lv],
        "icons": [_icon(f"level-{k}") for k in range(8)],
    }
    wid = "qplace-" + uuid.uuid4().hex[:8]
    html = f"""<style>{PLACE_CSS}</style>
<div class="qp" id="{wid}" data-qcai-widget="placement">
  <div class="qp-cta"><div class="ic">{_icon("compass")}</div>
    <div style="flex:1;min-width:14rem"><p><strong>Not sure where to start?</strong></p><small>A one-minute check suggests the right level for you.</small></div>
    <button type="button" class="qp-btn" data-act="open">Find my level</button></div>
  <div class="qp-chip"></div>
  <div class="qp-veil"><div class="qp-dlg" role="dialog" aria-modal="true" aria-labelledby="{wid}-t">
    <button type="button" class="qp-x" aria-label="Close">×</button>
    <div class="qp-head">{motion}</div><div class="qp-body"></div></div></div>
</div>
<script>{PLACE_JS.replace("__ID__", wid).replace("__DATA__", json.dumps(data, ensure_ascii=False))}</script>"""
    return HTML(html)
