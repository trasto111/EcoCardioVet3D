# -*- coding: utf-8 -*-
"""Ensambla ECOCARDIO 3D VET v1.2.

Salidas (carpeta dist/):
  ecocardio3d_v1.2.html               página del artefacto (sin <!doctype>: el publicador la envuelve)
  ecocardio3d_v1.2_web.html          la misma página con <!doctype>, para abrirla en un navegador (usa la CDN)
  test_wrapper.html                   copia de la anterior para las pruebas automáticas
  ecocardio3d_v1.2_sin_conexion.html  versión autónoma: Three.js y sus complementos empaquetados (sin CDN)

Uso:  python3 build.py            (requiere tools/node_modules con esbuild y three@0.160.0 para la versión sin conexión)
Todos los archivos se leen y escriben en UTF-8 de forma explícita.
"""
import base64, json, pathlib, subprocess, sys

R = pathlib.Path(__file__).resolve().parent
ENC = "utf-8"
rd = lambda p: (R / p).read_text(encoding=ENC)
b64 = lambda p: base64.b64encode((R / p).read_bytes()).decode("ascii")

HEART, THORAX = "build/heart_v05.glb", "build/thorax_v02.glb"
geo = json.loads(rd("build/geometry_meta.json"))
tor = json.loads(rd("build/thorax_meta.json"))
# revisión visual de cada preset frente a su referencia (Claude; pendiente de revisión veterinaria)
rev = json.loads(rd("model/revision_referencia.json"))
for v in tor["vistas"]: v["revision_referencia"] = rev.get(v["id"])
refs = json.loads(rd("refs/refs.json"))
# imágenes de referencia ANONIMIZADAS (cabecera con clínica, fecha y paciente tapada; sin metadatos JPEG)
refs = {k: {"src": "data:image/jpeg;base64," + b64("refs/anon/" + v["file"]), "cap": v["cap"], "pag": v["pag"]} for k, v in refs.items()}

structs = rd("viewer/structures.js").replace("export const", "const")
# sección «Patologías» (v1.2): datos, deformaciones e imágenes reales anonimizadas (refs/pato, generadas con refs/pato_imagenes.py)
structs += "\n" + rd("viewer/patologias.js").replace("export function", "function").replace("export const", "const")
structs += "\n" + rd("viewer/atlas.js").replace("export function", "function").replace("export const", "const")   # v1.2: atlas
anat = rd("build/anat_check.json")
pato_imgs = {f.stem: "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode("ascii") for f in sorted((R / "refs/pato").glob("*.jpg"))}
app = rd("viewer/app.js")
app = app.replace('"__GLB_B64__"', '"' + b64(HEART) + '"').replace('"__TGLB_B64__"', '"' + b64(THORAX) + '"')
app = app.replace("__GEO_JSON__", json.dumps(geo, ensure_ascii=False)).replace("__TOR_JSON__", json.dumps(tor, ensure_ascii=False)).replace("__REFS_JSON__", json.dumps(refs)).replace("__PATO_IMGS__", json.dumps(pato_imgs)).replace("__ANAT_JSON__", anat)
tpl = rd("viewer/index.src.html")
html = tpl.replace("/*__STRUCTURES__*/", structs).replace("/*__APP__*/", app)

out = R / "dist"; out.mkdir(exist_ok=True)
HEAD = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0">'
(out / "ecocardio3d_v1.2.html").write_text(html, encoding=ENC)
(out / "test_wrapper.html").write_text(HEAD + html + "</body></html>", encoding=ENC)
(out / "ecocardio3d_v1.2_web.html").write_text(HEAD + html + "</body></html>", encoding=ENC)   # para abrir en el navegador o en GitHub (usa la CDN)
print("HTML (artefacto):", len(html.encode(ENC)), "bytes")

# ---------------- versión sin conexión: esbuild empaqueta app + three + complementos en un único script clásico
tools = R / "tools"; esb = tools / "node_modules" / ".bin" / "esbuild"
if not esb.exists():
    print("AVISO: falta tools/node_modules (npm install esbuild@0.20.2 three@0.160.0 en tools/); no se genera la versión sin conexión")
    sys.exit(0)
entry = tools / "entry_v12.js"
entry.write_text(structs + "\n" + app, encoding=ENC)
bundle = tools / "bundle_v12.js"
subprocess.run([str(esb), str(entry), "--bundle", "--format=iife", "--minify", "--charset=utf8", "--legal-comments=none",
                "--alias:three/addons=three/examples/jsm", f"--outfile={bundle}"], cwd=tools, check=True)
js = bundle.read_text(encoding=ENC).replace("</script", "<\\/script")
i0 = html.index('<script type="importmap">'); i1 = html.index("</script>", html.index('<script type="module">')) + len("</script>")
offline = html[:i0] + "<script>" + js + "</script>" + html[i1:]
assert "cdn.jsdelivr.net/npm/three" not in offline
(out / "ecocardio3d_v1.2_sin_conexion.html").write_text(HEAD + offline + "</body></html>", encoding=ENC)
entry.unlink(); bundle.unlink()
print("HTML (sin conexión):", len(offline.encode(ENC)), "bytes")
