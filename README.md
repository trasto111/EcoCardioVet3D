# ECOCARDIO 3D VET

Simulador 3D interactivo para aprender ecocardiografía canina: corazón y tórax del perro en 3D, sonda virtual con el plano de corte, 13 vistas estándar, 5 patologías recreadas en 3D y un atlas para principiantes con hojas de medidas y velocidades.

> **Repositorio privado. Uso formativo.** Contiene imágenes clínicas de los apuntes del curso (anonimizadas: sin paciente, clínica, fecha ni metadatos) y datos parafraseados de bibliografía con derechos de autor. No lo hagas público ni redistribuyas las imágenes.

## Abrir la aplicación

| Archivo | Uso |
|---|---|
| `dist/ecocardio3d_v1.2_sin_conexion.html` | Descárgalo y ábrelo con doble clic. Funciona **sin Internet**. |
| `dist/ecocardio3d_v1.2_web.html` | La misma aplicación, cargando Three.js desde la CDN (necesita Internet). |
| `dist/ECOCARDIO_hoja_medidas_basica_v1.2.pdf` | Hoja de medidas y velocidades básica (A4). |
| `dist/ECOCARDIO_hoja_medidas_completa_v1.2.pdf` | Hoja completa (Cornell, cocientes, Doppler, gravedad). |
| `dist/ECOCARDIO_guia_principiantes_v1.2.pdf` | Guía de exploración para principiantes. |

GitHub no ejecuta los HTML al pulsarlos (muestra el código): usa el botón **Download raw file** y ábrelo en Chrome, Edge o Firefox.

## Modos (teclas 1–5)
1. **Explorar**: anatomía 3D, ocultar y resaltar estructuras, transparencia.
2. **Planos**: cortes anatómicos del modelo.
3. **Sonda**: colocar y mover el transductor en el tórax; imagen de sección y simulación ecográfica didáctica.
4. **Patologías**: EDVM, CMD, hipertensión pulmonar, CAP y estenosis pulmonar, con tres grados y medidas frente a los umbrales.
5. **Atlas**: guía para principiantes, 20 fichas de enfermedades, hojas de medidas con calculadora por peso, glosario y bibliografía.

La imagen ecográfica es una **sección geométrica del modelo con efecto visual**, no una simulación física de ultrasonidos.

## Estructura

```
model/    generación del corazón y del tórax (Python), criterios de las vistas, comprobaciones anatómicas
viewer/   interfaz (index.src.html, app.js), estructuras, patologías y contenido del atlas
refs/     imágenes de referencia anonimizadas y script que las regenera desde los PDF
build/    modelos GLB y metadatos generados
tools/    informes de validación y package.json (esbuild + three)
dist/     aplicación lista para abrir y PDF imprimibles
docs/     resúmenes de cada versión e informes de validación
build.py  ensambla los HTML de dist/
```

## Regenerar (Python 3.11+, Node 18+)

```bash
export PYTHONUTF8=1                  # Windows PowerShell: $env:PYTHONUTF8 = "1"
pip install numpy scipy scikit-image trimesh fast_simplification pillow
python model/build_heart.py build
python model/build_thorax.py build   # --recalibrar repite la calibración (~10 min)
python model/anat_check.py build
cd tools && npm install esbuild@0.20.2 three@0.160.0 && cd ..
python build.py
```

`refs/pato_imagenes.py <carpeta con los PDF del proyecto>` regenera las imágenes de patologías (necesita poppler).

## Estado (v1.2)
- Validado en navegador: 13 vistas, pruebas de regresión A1–A6, patologías P1–P8 y atlas T1–T7, sin fallos.
- Discrepancias conocidas: VHS del tórax esquemático 6,7 (referencia 9,7); masa miocárdica 110 g (162 g esperados para 20 kg).
- Detalle, fuentes con página y contradicciones entre documentos: `docs/RESUMEN_v1.2.md`.
