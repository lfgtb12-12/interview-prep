"""Render a validated spec to a standalone *staging-only* HTML lesson."""
import argparse
import html
import json
from pathlib import Path

from validate import load


def esc(value):
    return html.escape(str(value), quote=True)


STYLE = """
:root{color-scheme:dark;--bg:#101a28;--panel:#1b2c3d;--edge:#50677c;--ink:#eff9ff;--accent:#8ce5d1}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,sans-serif}
main{max-width:920px;margin:auto;padding:24px}header{padding:16px 24px;border-bottom:1px solid var(--edge)}
a{color:var(--accent)}section{border:1px solid var(--edge);background:var(--panel);border-radius:14px;padding:22px;margin:20px 0}
button{font:inherit;border:1px solid var(--accent);color:var(--ink);background:#24545e;border-radius:7px;padding:9px 12px;cursor:pointer}
button:focus-visible,input:focus-visible{outline:3px solid #ffd18a;outline-offset:2px}
.diagram{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:20px 0}
.diagram span{padding:9px 12px;border:2px solid var(--edge);border-radius:9px}
.diagram span.active{border-color:var(--accent);background:#176857}
fieldset{border:1px solid var(--edge);border-radius:10px;margin:12px 0}
.feedback{padding:8px 0;min-height:28px}
pre{white-space:pre-wrap;background:#101a28;border-radius:9px;padding:15px}
@media(max-width:640px){main{padding:12px}section{padding:15px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
"""

SCRIPT = """
(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("lesson-data").textContent);
  const key = "ai-textbook-factory-" + data.id + "-v1";
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch {}
  if (!saved || typeof saved !== "object" || Array.isArray(saved)) saved = {};
  const answers = saved.answers && typeof saved.answers === "object" ? saved.answers : {};
  function store() {
    try { localStorage.setItem(key, JSON.stringify({done: !!document.querySelector("#done").checked, answers})); } catch {}
  }
  document.querySelector("#done").checked = saved.done === true;
  document.querySelector("#done").addEventListener("change", store);
  document.querySelectorAll("[data-quiz]").forEach((form) => {
    const i = Number(form.dataset.quiz);
    if (Number.isInteger(answers[i]) && answers[i] >= 0 && answers[i] < 4) {
      const selected = form.querySelector('input[value="' + answers[i] + '"]');
      if (selected) selected.checked = true;
    }
    form.querySelector("button").addEventListener("click", () => {
      const selected = form.querySelector("input:checked");
      const feedback = form.querySelector(".feedback");
      if (!selected) { feedback.textContent = "Choose an answer first."; return; }
      const value = Number(selected.value);
      answers[i] = value;
      const q = data.quiz[i];
      feedback.textContent = (value === q.answer ? "Correct. " : "Not yet. ") + q.explanation;
      store();
    });
  });
  document.querySelectorAll("[data-diagram]").forEach((area) => {
    const diagram = data.sections[Number(area.dataset.diagram)].diagram;
    let index = 0;
    const nodes = [...area.querySelectorAll("[data-node]")];
    const message = area.querySelector("[data-current]");
    const update = () => {
      const current = diagram.edges[index];
      nodes.forEach((node) => node.classList.toggle("active", node.dataset.node === current[1]));
      message.textContent = current[0] + " → " + current[1] + " (" + (index+1) + "/" + diagram.edges.length + ")";
    };
    area.querySelector("button").addEventListener("click", () => { index = (index + 1) % diagram.edges.length; update(); });
    update();
  });
})();
"""


def render(data):
    chunks = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              f'<title>{esc(data["id"])} · {esc(data["title"])}</title><style>{STYLE}</style></head><body>',
              '<header><a href="../">← Handbook</a> · Generated preview · Not published</header><main>',
              f'<h1>{esc(data["title"])}</h1><p>{esc(data["summary"])}</p>',
              '<section><h2>Learning objectives</h2><ul>']
    chunks.extend(f'<li>{esc(item)}</li>' for item in data["objectives"])
    chunks.append('</ul></section>')
    for i, section in enumerate(data["sections"]):
        chunks.append(f'<section id="{esc(section["id"])}"><h2>{esc(section["title"])}</h2>')
        chunks.extend(f'<p>{esc(p)}</p>' for p in section["paragraphs"])
        if "diagram" in section:
            diagram = section["diagram"]
            chunks.append(f'<div data-diagram="{i}" aria-label="Interactive {esc(diagram["type"])} diagram">')
            chunks.append('<div class="diagram">')
            chunks.extend(f'<span data-node="{esc(node)}">{esc(node)}</span>' for node in diagram["nodes"])
            chunks.append('</div><p data-current role="status" aria-live="polite"></p><button type="button">Next transition →</button></div>')
        chunks.append('</section>')
    chunks.append('<section><h2>Hands-on lab</h2>')
    chunks.append(f'<h3>{esc(data["lab"]["title"])}</h3><ol>')
    chunks.extend(f'<li>{esc(step)}</li>' for step in data["lab"]["instructions"])
    chunks.append(f'</ol><p><strong>Expected:</strong> {esc(data["lab"]["expected"])}</p></section>')
    chunks.append('<section><h2>Interview practice</h2><ol>')
    chunks.extend(f'<li>{esc(prompt)}</li>' for prompt in data["interview"])
    chunks.append('</ol></section><section><h2>Knowledge check</h2>')
    for i, q in enumerate(data["quiz"]):
        chunks.append(f'<fieldset data-quiz="{i}"><legend>{i+1}. {esc(q["prompt"])}</legend>')
        for j, option in enumerate(q["options"]):
            chunks.append(f'<label><input type="radio" name="q{i}" value="{j}"> {esc(option)}</label>')
        chunks.append('<p><button type="button">Check answer</button></p><p class="feedback" role="status" aria-live="polite"></p></fieldset>')
    chunks.append('</section><section><label><input type="checkbox" id="done"> Mark lesson complete on this device</label></section></main>')
    # Escape HTML-sensitive characters in JSON embedded inside a script element.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    chunks.append(f'<script type="application/json" id="lesson-data">{payload}</script><script>{SCRIPT}</script></body></html>')
    return "\n".join(chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--out", required=True, help="Staging directory (must not be the published ai-engineering folder)")
    args = parser.parse_args()
    data = load(args.spec)
    output = Path(args.out).resolve()
    published = Path(__file__).resolve().parent.parent
    if output == published or published in output.parents:
        parser.error("output must be outside the published ai-engineering directory")
    output.mkdir(parents=True, exist_ok=True)
    path = output / (data["id"].lower() + ".html")
    path.write_text(render(data), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
