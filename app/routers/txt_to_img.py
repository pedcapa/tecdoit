# app/routers/txt_to_img.py ──────────────────────────────────────────────────────────────
"""
Text-to-Image API
─────────────────
Convierte texto con fragmentos $…$ / $$…$$ (fracciones a/b, potencias ^,
multiplicación implícita o con * ) en PNG (Helvetica, 150 dpi) **sin**
simplificar nada.

Ejemplos
--------
$(1/2)*(2/3)$      →  ½ · ⅔
$1/(a*2) + 2/3$    →  1 ∕ (2a) + ⅔   (¡ahora sin “1” extra!)
$a/b * b$          →  (a/b) · b
"""

# ———————————— imports básicos ———————————————————————————————
import io, re
from fastapi import Response, HTTPException, APIRouter, status
from pydantic import BaseModel

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"],
    "mathtext.fontset": "cm",
})

# —––––––––––– Router & esquema de payload –––––––––––—
router = APIRouter(prefix="/txt_to_img", tags=["Imagenes"])

class TextPayload(BaseModel):
    text: str

# ———————————— SymPy ———————————————————————————————
from sympy import latex
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)
_TRANSFORM = (
    standard_transformations
    + (implicit_multiplication_application, convert_xor)
)

# PNG transparente 1×1 como fallback (sólo cabecera + bloque mínimo)
MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x02\xd2"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


# ———————————— patch: mixtos k·1/n ———————————————————————————
#  Ahora soporta denominadores con letras, p. ej. “1 \frac{1}{2 a}”.
_MIXED = re.compile(
    r'(\d+)\s*(?:\\cdot\s*)?\\frac\{1\}\{([^{}]+?)\}'
)
def _fix_mixed(tex: str) -> str:
    """Convierte «k · 1/n» en «k/n» (itera hasta que ya no haya coincidencias)."""
    while True:
        new = _MIXED.sub(r'\\frac{\1}{\2}', tex)
        if new == tex:
            return tex
        tex = new

# ———————————— expr → LaTeX sin evaluar ——————————————————————
def to_latex(expr: str) -> str:
    """Traduce una sub-expresión a LaTeX sin simplificar productos."""
    expr = expr.strip()
    if "\\" in expr:        # El usuario ya incluyó LaTeX
        return expr
    try:
        sym = parse_expr(expr, transformations=_TRANSFORM, evaluate=False)
        return _fix_mixed(latex(sym))
    except Exception:       # Deja pasar lo que SymPy no entienda
        return expr

# ———————————— bloques $…$ / $$…$$ ———————————————————————
DISPLAY_RE = re.compile(r'\$\$\s*([\s\S]+?)\s*\$\$', re.S)
INLINE_RE  = re.compile(r'\$(.+?)\$', re.S)

def preprocess(raw: str) -> str:
    def disp(m): return f"${to_latex(m.group(1).strip())}$"
    tmp = DISPLAY_RE.sub(disp, raw)
    def inl(m): return f"${to_latex(m.group(1))}$"
    return INLINE_RE.sub(inl, tmp)

# ———————————— render PNG —————————————————————————————
DPI, MARGIN_INCH, FONTSIZE_PT = 150, 0.3, 30

def render_png(txt: str) -> bytes:
    fig = plt.figure(dpi=DPI)
    ax  = fig.add_axes([0, 0, 1, 1]); ax.axis("off")

    t = ax.text(0, 1, preprocess(txt), ha="left", va="top", fontsize=FONTSIZE_PT)

    fig.canvas.draw()
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer()) \
          .transformed(fig.dpi_scale_trans.inverted())
    w, h = bb.width + 2*MARGIN_INCH, bb.height + 2*MARGIN_INCH
    fig.set_size_inches(w, h)
    t.set_position((MARGIN_INCH / w, 1 - MARGIN_INCH / h))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


@router.post(
    "/",
    summary="Convierte texto (o LaTeX) a PNG",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}}
)
def txt_to_img(payload: TextPayload):
    if not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Texto vacío"
        )

    # ───── pipeline de renderizado con 2 intentos ──────────────
    try:
        png = render_png(payload.text)                              # ① intento normal
    except RuntimeError:
        try:
            png = render_png(payload.text.replace("$", ""))         # ② sin símbolos $
        except Exception:
            png = MINIMAL_PNG                                       # ③ PNG de 1×1 px
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error procesando LaTeX: {exc}"
        )

    return Response(
        content=png,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename=\"output.png\"'}
    )


@router.get(
    "/ping",
    summary="Healthcheck del router de txt_to_img",
    response_model=dict[str, str]
    )
def ping() -> dict[str, str]:
    return {"status": "ok"}
