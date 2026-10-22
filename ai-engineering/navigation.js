/* Shared navigation: curriculum.json is source of truth; no framework or build step. */
(()=>{"use strict";
const fallback=[["M01","LLM Engineering Foundations"],["M02","Python for AI Engineering"],["M03","AI Agents & Tool Calling"],["M04","RAG & Information Retrieval"],["M05","Evaluation & Experimentation"],["M06","State, Memory & Durable Execution"],["M07","Security, Integrations & Protocols"],["M08","AI Platform & Operations"],["M09","ML Fundamentals & Model Adaptation"],["M10","Advanced Agent Architecture"],["M11","AI System Design"],["M12","Portfolio & Interview Execution"]];
const path=location.pathname,isChapter=/chapter-agent\.html$/.test(path),base="./";
const el=(tag,attrs={},txt)=>{let n=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(txt!==undefined)n.textContent=txt;return n};
function progress(){try{return JSON.parse(localStorage.getItem("ai-handbook-progress-v1")||"{}")}catch{return {}}}
let root,drawer,backdrop;
function addLink(parent,label,url,selected=false){let a=el("a",{href:url},label);if(selected)a.setAttribute("aria-current","page");parent.append(a);return a}
function draw(modules){root.replaceChildren();let nav=el("nav",{"aria-label":"Handbook curriculum navigation",class:"handbook-nav"});
nav.append(el("h2",{},"AI Engineering Handbook"));
nav.append(el("div",{class:"nav-meta"},"Learn · Build · Interview · Get Hired"));
nav.append(el("div",{class:"nav-heading"},"Workspace"));
addLink(nav,"Overview / Dashboard","./",!isChapter);
addLink(nav,"Quizzes","./#quiz");addLink(nav,"Flashcards","./#cards");addLink(nav,"12-module roadmap","./#roadmap");
nav.append(el("div",{class:"nav-heading"},"Modules"));
modules.forEach(m=>{let d=el("details");if(m.id==="M03")d.open=true;
let s=el("summary",{} ,m.id+" · "+m.title);let badge=el("span",{class:"status"},m.id==="M03"?"1 lesson":"Planned");s.append(badge);d.append(s);let links=el("div",{class:"subnav"});
if(m.id==="M03"){let a=addLink(links,"01 · What Is an AI Agent?","./chapter-agent.html",isChapter);if(progress().done)a.append(el("span",{class:"nav-done"},"✓"));addLink(links,"Lesson quiz","./#quiz");}
else{links.append(el("div",{class:"nav-meta"},"Lessons coming soon"));}
d.append(links);nav.append(d)});
nav.append(el("div",{class:"nav-heading"},"Learning records"));nav.append(el("p",{class:"nav-meta"},"Progress is saved only in this browser. Export it from the dashboard to transfer devices."));
root.append(nav);
}
function mount(){document.body.classList.add(isChapter?"handbook-chapter":"handbook-home");
let oldAside=document.querySelector(".layout > aside");root=el("div",{class:"handbook-nav-frame"});
if(isChapter){document.body.insertBefore(root,document.querySelector("main"));}
else if(oldAside){oldAside.prepend(root)}else{document.body.prepend(root)}
drawer=el("button",{class:"handbook-drawer-button","aria-label":"Toggle curriculum navigation","aria-expanded":"false","aria-controls":"shared-curriculum-nav"},"☰ Contents");root.id="shared-curriculum-nav";backdrop=el("div",{class:"handbook-backdrop"});document.body.append(backdrop);document.body.prepend(drawer);
function close(){document.body.classList.remove("nav-open");drawer.setAttribute("aria-expanded","false");drawer.textContent="☰ Contents"}
drawer.addEventListener("click",()=>{let open=document.body.classList.toggle("nav-open");drawer.setAttribute("aria-expanded",String(open));drawer.textContent=open?"✕ Close":"☰ Contents"});
backdrop.addEventListener("click",close);document.addEventListener("keydown",e=>{if(e.key==="Escape")close()});root.addEventListener("click",e=>{if(e.target.closest("a"))close()});
draw(fallback.map(([id,title])=>({id,title})));
fetch(base+"curriculum.json",{cache:"no-cache"}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(d=>{if(Array.isArray(d.modules))draw(d.modules)}).catch(()=>{});
window.addEventListener("storage",()=>draw(fallback.map(([id,title])=>({id,title}))));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();