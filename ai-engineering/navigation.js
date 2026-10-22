/* Curriculum-driven shared navigation. Compatible with historical localStorage keys. */
(()=>{"use strict";
const fallback=[[ "M01","LLM Engineering Foundations"],["M02","Python for AI Engineering"],["M03","AI Agents & Tool Calling"],["M04","RAG & Information Retrieval"],["M05","Evaluation & Experimentation"],["M06","State, Memory & Durable Execution"],["M07","Security, Integrations & Protocols"],["M08","AI Platform & Operations"],["M09","ML Fundamentals & Model Adaptation"],["M10","Advanced Agent Architecture"],["M11","AI System Design"],["M12","Portfolio & Interview Execution"]];
const defaultModules=fallback.map(([id,title])=>({id,title,lessons:[]}));
const file=location.pathname.split("/").pop()||"index.html",isChapter=file.startsWith("chapter-");
const el=(tag,attrs={},txt)=>{const n=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(txt!==undefined)n.textContent=txt;return n};
const read=(key)=>{try{const v=JSON.parse(localStorage.getItem(key)||"{}");return v&&typeof v==="object"?v:{}}catch{return {}}};
function completed(id){
  if(id==="M03-L01")return read("ai-handbook-progress-v1").done===true;
  return read("ai-handbook-"+id.toLowerCase()+"-v1").done===true;
}
function usablePath(value){return typeof value==="string"&&/^[a-z0-9][a-z0-9._/-]*\.html$/i.test(value)&&!value.includes("..")&&!value.startsWith("/");}
function validModules(modules){
  if(!Array.isArray(modules))return false;
  const ids=new Set(),paths=new Set();
  for(const m of modules){
    if(!m||typeof m.id!=="string"||!/^M\d{2}$/.test(m.id)||typeof m.title!=="string"||ids.has(m.id)||!Array.isArray(m.lessons))return false;
    ids.add(m.id);
    for(const lesson of m.lessons){
      if(!lesson||typeof lesson.id!=="string"||!new RegExp("^"+m.id+"-L\\d{2}$").test(lesson.id)||typeof lesson.title!=="string"||!usablePath(lesson.path)||paths.has(lesson.path))return false;
      paths.add(lesson.path);
    }
  }
  return true;
}
let root,drawer,backdrop,current=defaultModules;
function addLink(parent,label,url,selected=false){const a=el("a",{href:url},label);if(selected)a.setAttribute("aria-current","page");parent.append(a);return a}
function draw(modules){
 root.replaceChildren();const nav=el("nav",{"aria-label":"Handbook curriculum navigation",class:"handbook-nav"});
 nav.append(el("h2",{},"AI Engineering Handbook"),el("div",{class:"nav-meta"},"Learn · Build · Interview · Get Hired"),el("div",{class:"nav-heading"},"Workspace"));
 addLink(nav,"Overview / Dashboard","./",!isChapter);
 addLink(nav,"Quizzes","./#quiz");addLink(nav,"Flashcards","./#cards");addLink(nav,"12-module roadmap","./#roadmap");
 nav.append(el("div",{class:"nav-heading"},"Modules"));
 for(const m of modules){
   const d=el("details");if(m.id==="M03"||m.lessons.some(l=>l.path===file))d.open=true;
   const s=el("summary",{},m.id+" · "+m.title);
   const count=m.lessons.length;
   s.append(el("span",{class:"status"},count?count+" lesson"+(count===1?"":"s"):"Planned"));d.append(s);
   const links=el("div",{class:"subnav"});
   if(!count)links.append(el("div",{class:"nav-meta"},"Lessons coming soon"));
   for(const lesson of m.lessons){
      const n=lesson.id.split("-L")[1];
      const link=addLink(links,n+" · "+lesson.title,"./"+lesson.path,lesson.path===file);
      if(completed(lesson.id))link.append(el("span",{class:"nav-done"},"✓"));
   }
   if(m.id==="M03")addLink(links,"Lesson quiz","./#quiz");
   d.append(links);nav.append(d);
 }
 nav.append(el("div",{class:"nav-heading"},"Learning records"),el("p",{class:"nav-meta"},"Progress is saved only in this browser. Export it from the dashboard to transfer devices."));
 root.append(nav);
}
function mount(){
 document.body.classList.add(isChapter?"handbook-chapter":"handbook-home");
 const oldAside=document.querySelector(".layout > aside");root=el("div",{class:"handbook-nav-frame"});
 const main=document.querySelector("main");
 if(isChapter&&main)document.body.insertBefore(root,main);else if(oldAside)oldAside.prepend(root);else document.body.prepend(root);
 drawer=el("button",{class:"handbook-drawer-button","aria-label":"Toggle curriculum navigation","aria-expanded":"false","aria-controls":"shared-curriculum-nav"},"☰ Contents");
 root.id="shared-curriculum-nav";backdrop=el("div",{class:"handbook-backdrop"});document.body.append(backdrop);document.body.prepend(drawer);
 function close(){document.body.classList.remove("nav-open");drawer.setAttribute("aria-expanded","false");drawer.textContent="☰ Contents"}
 drawer.addEventListener("click",()=>{const open=document.body.classList.toggle("nav-open");drawer.setAttribute("aria-expanded",String(open));drawer.textContent=open?"✕ Close":"☰ Contents"});
 backdrop.addEventListener("click",close);document.addEventListener("keydown",e=>{if(e.key==="Escape")close()});root.addEventListener("click",e=>{if(e.target.closest("a"))close()});
 draw(current);
 fetch("./curriculum.json",{cache:"no-cache"}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(data=>{
  if(validModules(data.modules)){current=data.modules;draw(current)}
 }).catch(()=>{});
 window.addEventListener("storage",()=>draw(current));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();