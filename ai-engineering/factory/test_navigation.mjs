// Dependency-free browser-navigation smoke tests; run: node --test ai-engineering/factory/test_navigation.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root = new URL('../', import.meta.url);
const script = fs.readFileSync(new URL('navigation.js', root), 'utf8');
const manifest = JSON.parse(fs.readFileSync(new URL('curriculum.json', root), 'utf8'));

function element(tag) {
  return {
    tag,attrs:{},children:[],textContent:'',classList:{add(){},remove(){},toggle(){return true}},
    setAttribute(k,v){this.attrs[k]=v},
    append(...nodes){this.children.push(...nodes)},prepend(...nodes){this.children.unshift(...nodes)},
    replaceChildren(...nodes){this.children=[...nodes]},
    addEventListener(){},querySelector(){return null},
    closest(){return null}
  };
}
function tree(node) { return [node,...(node.children||[]).flatMap(tree)]; }
function simulate(data,storage={},pathname='/interview-prep/ai-engineering/chapter-agent.html') {
  const body=element('body');
  const main=element('main');
  body.children=[main];body.insertBefore=(newNode,reference)=>{body.children.splice(body.children.indexOf(reference),0,newNode)};
  body.querySelector=()=>null;
  const doc={body,readyState:'complete',createElement:element,querySelector:q=>q==='main'?main:null,addEventListener(){}};
  const localStorage={getItem:k=>storage[k]||null};
  const context={document:doc,location:{pathname},localStorage,window:{addEventListener(){}},
    fetch:async()=>({ok:true,json:async()=>data})};
  vm.runInNewContext(script,context);
  return new Promise(resolve=>setImmediate(()=>resolve(tree(body))));
}
function links(nodes){return nodes.filter(n=>n.tag==='a')}
test('manifest defines unique valid M03 lesson paths',()=>{
  const m03=manifest.modules.find(m=>m.id==='M03');
  assert.equal(m03.lessons.length,4);
  const paths=m03.lessons.map(l=>l.path);
  assert.equal(new Set(paths).size,paths.length);
  for(const path of paths)assert.equal(fs.existsSync(new URL(path,root)),true,path);
});
test('sidebar uses manifest lesson title and path, highlighting current chapter',async()=>{
  const nodes=await simulate(manifest);
  const anchors=links(nodes);
  for(const lesson of manifest.modules.find(m=>m.id==='M03').lessons){
    const a=anchors.find(a=>a.attrs.href==='./'+lesson.path);
    assert.ok(a,lesson.id);
    assert.ok(a.textContent.includes(lesson.title));
  }
  assert.equal(anchors.find(a=>a.attrs.href==='./chapter-agent.html').attrs['aria-current'],'page');
});
test('historical completion keys still produce checkmarks',async()=>{
  const nodes=await simulate(manifest,{
    'ai-handbook-progress-v1':JSON.stringify({done:true}),
    'ai-handbook-m03-l02-v1':JSON.stringify({done:true}),
  });
  for(const name of ['chapter-agent.html','chapter-tool-contracts.html']){
    const a=links(nodes).find(a=>a.attrs.href==='./'+name);
    assert.ok(a.children.some(n=>n.textContent==='✓'),name);
  }
});
test('new lesson appears from manifest without code changes',async()=>{
  const data=structuredClone(manifest);
  data.modules.find(m=>m.id==='M04').lessons=[{id:'M04-L01',title:'A New Retrieval Lesson',path:'chapter-retrieval.html'}];
  const nodes=await simulate(data,{},'/interview-prep/ai-engineering/chapter-retrieval.html');
  const a=links(nodes).find(a=>a.attrs.href==='./chapter-retrieval.html');
  assert.ok(a);
  assert.equal(a.attrs['aria-current'],'page');
});
test('unsafe manifest paths are rejected',async()=>{
  const data=structuredClone(manifest);
  data.modules[2].lessons[0].path='../index.html';
  const nodes=await simulate(data);
  assert.equal(links(nodes).some(a=>a.attrs.href==='./../index.html'),false);
});
