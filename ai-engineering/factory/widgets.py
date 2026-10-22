"""Interactive timeline, retry, and parameter exercise components."""
WIDGET_CSS = """
.widget{background:#13293a;border:1px solid var(--edge);border-radius:12px;padding:18px;margin:18px 0}
.widget label{display:block;margin:10px 0}.widget input[type=range]{width:240px;max-width:100%;vertical-align:middle}
.widget select{padding:7px;background:#223e53;color:white;border:1px solid #94b6c7;border-radius:7px}
.widget .lanes{display:grid;gap:8px}.widget .lane{display:grid;grid-template-columns:115px minmax(0,1fr);gap:10px;align-items:center}
.widget .track{height:38px;position:relative;background:#0d2031;border:1px solid #39536d;border-radius:6px}
.widget .bar{position:absolute;top:4px;height:28px;background:#288d81;border-radius:5px;transition:left .25s,width .25s;padding:2px 5px;font-size:12px;overflow:hidden;white-space:nowrap}
.widget .bar.failed{background:#a34f57}.widget output{font-weight:700;color:#b0f5e7}
.widget .choices{display:flex;flex-wrap:wrap;gap:8px}.widget button:disabled{opacity:.45}
.widget .attempts{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}.widget .attempt{padding:7px 12px;border-radius:7px;background:#2b4356}
.widget .attempt.active{background:#a36331}.widget .attempt.done{background:#18715b}
@media(max-width:600px){.widget .lane{grid-template-columns:75px minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){.widget .bar{transition:none}}
"""
WIDGET_JS = """
function mountWidget(area, spec) {
 const out=area.querySelector('output');
 const kind=spec.type;
 if(kind==='timeline'){
   const strategy=area.querySelector('[data-strategy]');
   const speed=area.querySelector('[data-speed]');
   const lanes=area.querySelector('[data-lanes]');
   function render(){
     const tasks=spec.tasks;
     const total=tasks.reduce((m,t)=>Math.max(m,t.start+t.duration),0);
     let cursor=0;
     lanes.replaceChildren();
     tasks.forEach(t=>{
       const start=strategy.value==='parallel'?t.start:cursor;
       if(strategy.value!=='parallel')cursor+=t.duration;
       const row=document.createElement('div');row.className='lane';
       const label=document.createElement('span');label.textContent=t.name;
       const track=document.createElement('div');track.className='track';
       const bar=document.createElement('div');bar.className='bar';bar.textContent=t.duration+'s';
       bar.style.left=(start/(strategy.value==='parallel'?total:tasks.reduce((s,t)=>s+t.duration,0))*100)+'%';
       bar.style.width=(t.duration/(strategy.value==='parallel'?total:tasks.reduce((s,t)=>s+t.duration,0))*100)+'%';
       track.append(bar);row.append(label,track);lanes.append(row);
     });
     const duration=strategy.value==='parallel'?total:cursor;
     out.textContent='Makespan: '+(duration/Number(speed.value)).toFixed(1)+'s (illustrative speed multiplier)';
   }
   strategy.addEventListener('change',render);speed.addEventListener('input',render);render();
 } else if(kind==='retry'){
   const attemptArea=area.querySelector('[data-attempts]');
   const state=area.querySelector('[data-state]');
   const next=area.querySelector('[data-next]');
   const reset=area.querySelector('[data-reset]');
   let attempt=0;
   function update(){
     attemptArea.replaceChildren();
     for(let i=0;i<spec.maxAttempts;i++){
       const el=document.createElement('span');
       el.className='attempt'+(i<attempt?' done':i===attempt?' active':'');
       el.textContent='Attempt '+(i+1);attemptArea.append(el);
     }
     const unknown=spec.outcome==='unknown';
     state.textContent=attempt===0?'Ready to run':
       unknown?'UNKNOWN: do not replay without reconciliation':
       attempt>=spec.failuresBeforeSuccess+1?'SUCCEEDED after '+attempt+' attempt(s)':
       attempt>=spec.maxAttempts?'FAILED: retry budget exhausted':'Transient failure: retry allowed';
     next.disabled=unknown&&attempt>0||attempt>=spec.maxAttempts||(!unknown&&attempt>spec.failuresBeforeSuccess);
     out.textContent=state.textContent;
   }
   next.addEventListener('click',()=>{attempt++;update()});
   reset.addEventListener('click',()=>{attempt=0;update()});update();
 } else if(kind==='parameter'){
   const input=area.querySelector('[data-value]');
   const submit=area.querySelector('[data-check]');
   const answer=area.querySelector('[data-answer]');
   function calculate(v){return spec.base+v*spec.factor}
   function redraw(){out.textContent=spec.parameter+': '+input.value;answer.textContent='';}
   input.addEventListener('input',redraw);
   submit.addEventListener('click',()=>{
     answer.textContent=calculate(Number(input.value))===spec.target?'Correct. '+spec.explanation:
       'Not yet: computed result '+calculate(Number(input.value))+'. '+spec.explanation;
   });redraw();
 }
}
"""
