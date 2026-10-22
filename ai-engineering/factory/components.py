"""Reusable, dependency-free rendered interactive components.

All student-authored strings are escaped in render.py. Components only supply
static markup, CSS, and JavaScript; no execution of lesson content.
"""
COMPONENT_CSS = """
.simulator{background:#122537;border:1px solid var(--edge);border-radius:12px;padding:16px;margin:16px 0}
.sim-graph{width:100%;height:auto;max-height:340px;display:block}
.sim-edge{stroke:#8299ad;stroke-width:3;stroke-dasharray:8 6;opacity:.5}
.sim-edge.active{stroke:#8ce5d1;opacity:1;animation:dash 1s linear infinite}
.sim-node rect{fill:#29415a;stroke:#8299ad;stroke-width:2;transition:fill .2s}
.sim-node.active rect{fill:#176857;stroke:#8ce5d1;stroke-width:3}
.sim-node text{font:13px system-ui,sans-serif;fill:white;text-anchor:middle}
.sim-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.sim-stage{background:#0e1c2b;border-radius:8px;padding:10px;margin-top:12px}
.sim-progress{height:9px;background:#243a50;border-radius:99px;overflow:hidden}
.sim-progress div{height:100%;width:0;background:#8ce5d1;transition:width .25s}
.sim-status{min-height:26px}
.sim-caption{color:#bdd6e7;font-size:.95rem}
.sim-step-list{margin:10px 0}
.sim-step-list li[aria-current=step]{color:#aaf6e6;font-weight:700}
@keyframes dash{to{stroke-dashoffset:-28}}
@media(prefers-reduced-motion:reduce){.sim-edge.active{animation:none}.sim-progress div,.sim-node rect{transition:none}}
"""
COMPONENT_JS = """
function mountSimulation(area, diagram) {
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = area.querySelector('svg');
  const count = diagram.nodes.length;
  const centerY = 95, width = 760;
  const positions = new Map();
  diagram.nodes.forEach((name,i) => {
    const x = count === 1 ? width/2 : 90 + i * (width-180)/(count-1);
    positions.set(name,{x,y:centerY});
  });
  function svgEl(tag, attrs) {
    const node = document.createElementNS(svgNS,tag);
    Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,String(v)));
    return node;
  }
  const edges = diagram.edges.map(([from,to]) => {
    const a=positions.get(from),b=positions.get(to);
    const line=svgEl('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,class:'sim-edge'});
    svg.append(line);
    return line;
  });
  const nodes = new Map();
  diagram.nodes.forEach(name=>{
    const p=positions.get(name);
    const g=svgEl('g',{class:'sim-node'});
    const rect=svgEl('rect',{x:p.x-72,y:p.y-28,width:144,height:56,rx:10});
    const label=svgEl('text',{x:p.x,y:p.y+5});
    // SVG textContent prevents HTML injection from lesson data.
    label.textContent=name.length>20 ? name.slice(0,19)+'…' : name;
    g.append(rect,label);svg.append(g);nodes.set(name,g);
  });
  const status=area.querySelector('[data-current]');
  const bar=area.querySelector('[data-progress]');
  const list=area.querySelector('[data-steps]');
  const buttons={back:area.querySelector('[data-prev]'),next:area.querySelector('[data-next]'),reset:area.querySelector('[data-reset]')};
  let index=-1;
  diagram.edges.forEach(([from,to],i)=>{
    const li=document.createElement('li');
    li.textContent=from+' → '+to;
    li.setAttribute('data-step',i);
    list.append(li);
  });
  function redraw(){
    edges.forEach((e,i)=>e.classList.toggle('active',i===index));
    nodes.forEach((node,name)=>node.classList.toggle('active',index>=0&&diagram.edges[index][1]===name));
    const step=index+1;
    bar.style.width=(100*step/diagram.edges.length)+'%';
    area.setAttribute('data-step',String(step));
    status.textContent=index<0?'Ready. Choose Next to trace the first transition.':
      diagram.edges[index][0]+' → '+diagram.edges[index][1]+' · '+step+'/'+diagram.edges.length;
    [...list.children].forEach((li,i)=>{
      if(i===index)li.setAttribute('aria-current','step');
      else li.removeAttribute('aria-current');
    });
    buttons.back.disabled=index<0;
    buttons.next.disabled=index===diagram.edges.length-1;
  }
  buttons.back.addEventListener('click',()=>{index=Math.max(-1,index-1);redraw()});
  buttons.next.addEventListener('click',()=>{index=Math.min(diagram.edges.length-1,index+1);redraw()});
  buttons.reset.addEventListener('click',()=>{index=-1;redraw()});
  redraw();
}
"""
