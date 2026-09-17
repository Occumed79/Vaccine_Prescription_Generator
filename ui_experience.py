from __future__ import annotations

import base64
from pathlib import Path

ASSET_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSET_DIR / "occu-med-logo.webp"
VIALS = [
    ("vial-purple.webp", "174, 82, 255", "purple"),
    ("vial-green.webp", "58, 255, 95", "green"),
    ("vial-blue.webp", "42, 165, 255", "blue"),
    ("vial-cyan.webp", "41, 238, 240", "cyan"),
    ("vial-green-alt.webp", "67, 255, 151", "emerald"),
]


def _asset_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    suffix = path.suffix.lower().lstrip(".") or "png"
    mime = "image/svg+xml" if suffix == "svg" else f"image/{suffix}"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def apply_luminous_ui() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
          --om-blue: #1B4079;
          --om-air: #4D7C8A;
          --om-cambridge: #7F9C96;
          --om-mindaro: #CBDF90;
          --om-charcoal: #1C282E;
          --om-mist: #ACC8C9;
          --text-main: rgba(248, 251, 255, .97);
          --text-soft: rgba(228, 238, 244, .78);
        }
        html, body, .stApp { min-height: 100%; }
        .stApp {
          color: var(--text-main);
          background:
            radial-gradient(circle at 12% 6%, rgba(77,124,138,.26), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(27,64,121,.28), transparent 34%),
            linear-gradient(135deg, #15232a 0%, #08111e 52%, #04070d 100%);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stStatusWidget"] { background: transparent !important; }
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { visibility: hidden !important; height: 0 !important; }
        footer { visibility: hidden !important; }
        .block-container { position: relative; z-index: 1; max-width: 1180px; padding-top: 2.2rem; }
        h1, h2, h3, p, label, span, [data-testid="stMarkdownContainer"] * { color: var(--text-main) !important; }
        .hero, div[data-testid="stFileUploader"] section, div[data-testid="stDataFrame"] {
          border: 1px solid rgba(172,200,201,.24) !important;
          border-radius: 26px !important;
          background: linear-gradient(135deg, rgba(172,200,201,.11), rgba(27,64,121,.17) 46%, rgba(28,40,46,.45)) !important;
          box-shadow: 0 24px 80px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.10) !important;
          backdrop-filter: blur(20px) saturate(145%);
          -webkit-backdrop-filter: blur(20px) saturate(145%);
        }
        .hero { padding: 32px 38px; margin-bottom: 20px; }
        .hero h1 { margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.1rem); letter-spacing: -.045em; }
        .hero p { margin: 0; color: var(--text-soft) !important; line-height: 1.65; }
        code { color: #dff8ff !important; background: rgba(5,10,18,.58); border-radius: 7px; padding: .12rem .32rem; }
        input, textarea, [data-baseweb="select"], [data-baseweb="input"] {
          color: #f8fbff !important;
          background: rgba(5,10,18,.78) !important;
          border-color: rgba(172,200,201,.30) !important;
        }
        .stButton > button, .stDownloadButton > button, [data-testid="stFileUploader"] button {
          border-radius: 15px !important;
          border: 1px solid rgba(172,200,201,.34) !important;
          color: #f8fbff !important;
          background: linear-gradient(135deg, rgba(77,124,138,.88), rgba(27,64,121,.78)) !important;
          box-shadow: 0 0 30px rgba(77,124,138,.18) !important;
          font-weight: 800 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _vial_markup() -> str:
    parts: list[str] = []
    for index, (filename, rgb, name) in enumerate(VIALS):
        src = _asset_data_uri(ASSET_DIR / filename)
        image = (
            f'<img src="{src}" alt="Glowing {name} vaccine vial" draggable="false" />'
            if src
            else f'<div class="vial-fallback">{name}</div>'
        )
        parts.append(
            f'<div class="vial-shell v{index + 1}" style="--rgb:{rgb}" '
            f'data-rgb="{rgb}" data-source="{filename}">{image}</div>'
        )
    return "".join(parts)


def _build_landing_html() -> str:
    logo_src = _asset_data_uri(LOGO_PATH)
    logo_html = (
        f'<img class="brand-image" src="{logo_src}" alt="Occu-Med logo" data-source="occu-med-logo.webp" />'
        if logo_src
        else '<div class="brand-fallback" data-source="occu-med-logo.webp">OCCU-MED</div>'
    )
    vials = _vial_markup()

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0; width: 100%; height: 100%; overflow: hidden;
      background: #03070d;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .stage {{
      position: relative; width: 100vw; height: 100vh; overflow: hidden;
      display: grid; place-items: center;
      background:
        radial-gradient(circle at 50% 52%, rgba(24, 66, 104, .23), transparent 36%),
        radial-gradient(circle at 13% 34%, rgba(119, 54, 190, .08), transparent 27%),
        radial-gradient(circle at 88% 36%, rgba(14, 162, 152, .08), transparent 29%),
        linear-gradient(135deg, #142128 0%, #07101d 48%, #03070d 100%);
      isolation: isolate;
    }}
    .stage::before {{
      content: ""; position: absolute; inset: -15%; pointer-events: none; z-index: 0;
      background:
        radial-gradient(ellipse at 50% 62%, rgba(30, 108, 177, .17), transparent 42%),
        linear-gradient(118deg, transparent 20%, rgba(77,124,138,.11) 43%, rgba(172,200,201,.08) 51%, transparent 69%);
      filter: blur(22px);
      animation: atmosphere 20s ease-in-out infinite alternate;
    }}
    #particle-field {{ position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }}
    .frame {{
      position: absolute; inset: 18px; z-index: 5; pointer-events: none;
      border: 1px solid rgba(172,200,201,.20); border-radius: 42px;
      box-shadow: 0 34px 120px rgba(0,0,0,.50), inset 0 1px 0 rgba(255,255,255,.10);
      background: linear-gradient(145deg, rgba(255,255,255,.015), rgba(255,255,255,0));
      backdrop-filter: blur(1.5px);
    }}
    .frame::after {{
      content: ""; position: absolute; inset: 18px; border-radius: 30px;
      border: 1px solid rgba(255,255,255,.075);
    }}
    .scene {{
      position: relative; z-index: 3; width: min(1180px, 92vw); height: min(760px, 88vh);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      gap: clamp(16px, 3vh, 34px); pointer-events: none;
    }}
    .brand-wrap {{
      position: relative; z-index: 6; width: min(530px, 52vw); display: grid; place-items: center;
      min-height: 120px;
    }}
    .brand-wrap::before {{
      content: ""; position: absolute; width: 115%; height: 120%; border-radius: 50%;
      background: radial-gradient(ellipse, rgba(172,200,201,.18), rgba(27,64,121,.08) 45%, transparent 72%);
      filter: blur(20px); opacity: .7;
    }}
    .brand-image {{
      position: relative; display: block; width: 100%; max-height: 180px; object-fit: contain;
      filter: drop-shadow(0 0 18px rgba(172,200,201,.38)) drop-shadow(0 0 36px rgba(27,64,121,.32));
    }}
    .brand-fallback {{
      position: relative; color: white; font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 800;
      letter-spacing: .12em; text-shadow: 0 0 30px rgba(172,200,201,.4);
    }}
    .vial-lineup {{
      position: relative; width: min(1120px, 92vw); height: min(410px, 50vh);
      display: flex; align-items: flex-end; justify-content: center; gap: clamp(2px, 1.35vw, 18px);
      z-index: 4; overflow: visible;
    }}
    .vial-shell {{
      --rgb: 42, 165, 255;
      position: relative; height: 90%; flex: 0 1 19%; min-width: 0;
      display: flex; align-items: flex-end; justify-content: center;
      filter: drop-shadow(0 0 10px rgba(var(--rgb), .38));
    }}
    .vial-shell::before {{
      content: ""; position: absolute; left: 50%; bottom: 4%; width: 92%; height: 88%;
      transform: translateX(-50%) scale(.86); border-radius: 48%; z-index: -1;
      background:
        radial-gradient(ellipse at 50% 62%, rgba(var(--rgb), .38), rgba(var(--rgb), .14) 39%, transparent 70%),
        radial-gradient(ellipse at 50% 78%, rgba(var(--rgb), .24), transparent 64%);
      filter: blur(22px); opacity: .62;
      animation: auraBreath 5.8s ease-in-out infinite;
      animation-delay: calc(var(--i, 0) * -.7s);
    }}
    .vial-shell::after {{
      content: ""; position: absolute; left: 50%; bottom: -2%; width: 62%; height: 12%;
      transform: translateX(-50%); border-radius: 50%;
      background: radial-gradient(ellipse, rgba(var(--rgb), .46), transparent 68%);
      filter: blur(15px); opacity: .5;
      animation: groundlessPulse 5.8s ease-in-out infinite;
    }}
    .vial-shell img {{
      display: block; width: 100%; height: 100%; object-fit: contain; object-position: center bottom;
      user-select: none; -webkit-user-drag: none;
    }}
    .v1 {{ --i: 0; height: 82%; }}
    .v2 {{ --i: 1; height: 91%; }}
    .v3 {{ --i: 2; height: 100%; flex-basis: 22%; }}
    .v4 {{ --i: 3; height: 91%; }}
    .v5 {{ --i: 4; height: 83%; }}
    .vial-fallback {{ color: rgba(var(--rgb), .9); font-weight: 800; text-transform: uppercase; }}
    .open-link {{ position: absolute; inset: 0; z-index: 20; cursor: pointer; }}

    @keyframes auraBreath {{
      0%, 100% {{ transform: translateX(-50%) scale(.84); opacity: .36; filter: blur(19px); }}
      50% {{ transform: translateX(-50%) scale(1.08); opacity: .74; filter: blur(28px); }}
    }}
    @keyframes groundlessPulse {{
      0%, 100% {{ opacity: .26; transform: translateX(-50%) scale(.85); }}
      50% {{ opacity: .62; transform: translateX(-50%) scale(1.08); }}
    }}
    @keyframes atmosphere {{
      0% {{ transform: translate3d(-4%, -2%, 0) scale(1.01); opacity: .64; }}
      100% {{ transform: translate3d(5%, 2%, 0) scale(1.07); opacity: .92; }}
    }}

    @media (max-width: 820px) {{
      .frame {{ inset: 10px; border-radius: 28px; }}
      .frame::after {{ inset: 10px; border-radius: 20px; }}
      .scene {{ width: 96vw; height: 92vh; gap: 12px; }}
      .brand-wrap {{ width: min(480px, 68vw); min-height: 88px; }}
      .vial-lineup {{ width: 96vw; height: min(370px, 48vh); gap: 0; transform: scale(.96); }}
      .vial-shell {{ flex-basis: 20%; }}
      .v3 {{ flex-basis: 22%; }}
    }}
    @media (max-width: 540px) {{
      .brand-wrap {{ width: 76vw; }}
      .vial-lineup {{ width: 104vw; transform: scale(.82); transform-origin: center center; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .stage::before, .vial-shell::before, .vial-shell::after {{ animation: none !important; }}
      .vial-shell::before {{ opacity: .48; transform: translateX(-50%) scale(.95); }}
    }}
  </style>
</head>
<body>
  <div class="stage">
    <canvas id="particle-field" aria-hidden="true"></canvas>
    <div class="frame"></div>
    <div class="scene">
      <div class="brand-wrap">{logo_html}</div>
      <div class="vial-lineup">{vials}</div>
    </div>
    <a class="open-link" href="?view=app" target="_parent" aria-label="Open vaccine prescription generator"></a>
  </div>
  <script>
    (() => {{
      const canvas = document.getElementById('particle-field');
      const ctx = canvas.getContext('2d', {{ alpha: true }});
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
      const colors = [
        [174, 82, 255],
        [58, 255, 95],
        [42, 165, 255],
        [41, 238, 240],
        [67, 255, 151]
      ];
      const stops = [0.26, 0.38, 0.50, 0.62, 0.74];
      let particles = [];
      let width = 0;
      let height = 0;
      let dpr = 1;
      let frameId = null;

      function nearestColor(x) {{
        const t = x / Math.max(width, 1);
        let best = 0;
        let distance = Infinity;
        for (let i = 0; i < stops.length; i++) {{
          const current = Math.abs(t - stops[i]);
          if (current < distance) {{ distance = current; best = i; }}
        }}
        return colors[best];
      }}

      function makeParticle(staticMode = false) {{
        const depth = .35 + Math.random() * .85;
        const x = Math.random() * width;
        const color = nearestColor(x);
        return {{
          x,
          y: Math.random() * height,
          vx: staticMode ? 0 : (Math.random() - .5) * .11 * depth,
          vy: staticMode ? 0 : -(0.05 + Math.random() * .18) * depth,
          r: (0.55 + Math.random() * 1.65) * depth,
          a: 0.10 + Math.random() * .42,
          blur: Math.random() < .18 ? 7 + Math.random() * 8 : 0,
          color,
          phase: Math.random() * Math.PI * 2,
          bloom: Math.random() < .055
        }};
      }}

      function resize() {{
        const rect = canvas.getBoundingClientRect();
        width = rect.width;
        height = rect.height;
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.max(1, Math.floor(width * dpr));
        canvas.height = Math.max(1, Math.floor(height * dpr));
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const count = Math.max(85, Math.min(220, Math.round((width * height) / 6500)));
        particles = Array.from({{ length: count }}, () => makeParticle(reducedMotion.matches));
        draw(0, true);
      }}

      function draw(time = 0, staticOnly = false) {{
        ctx.clearRect(0, 0, width, height);
        ctx.globalCompositeOperation = 'lighter';
        for (const p of particles) {{
          if (!staticOnly && !reducedMotion.matches) {{
            p.x += p.vx;
            p.y += p.vy;
            p.phase += .008;
            if (p.y < -18) {{ p.y = height + 18; p.x = Math.random() * width; p.color = nearestColor(p.x); }}
            if (p.x < -18) p.x = width + 18;
            if (p.x > width + 18) p.x = -18;
          }}
          const pulse = p.bloom ? .65 + Math.sin(p.phase + time * .0015) * .35 : .88 + Math.sin(p.phase) * .12;
          const [r, g, b] = p.color;
          ctx.save();
          ctx.shadowBlur = p.blur + (p.bloom ? 12 * pulse : 0);
          ctx.shadowColor = `rgba(${{r}}, ${{g}}, ${{b}}, ${{Math.min(.85, p.a + .22)}})`;
          ctx.fillStyle = `rgba(${{r}}, ${{g}}, ${{b}}, ${{Math.max(.04, p.a * pulse)}})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * (p.bloom ? 1.35 : 1), 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }}
        ctx.globalCompositeOperation = 'source-over';
        if (!staticOnly && !reducedMotion.matches) frameId = requestAnimationFrame(draw);
      }}

      function restart() {{
        if (frameId) cancelAnimationFrame(frameId);
        frameId = null;
        resize();
        if (!reducedMotion.matches) frameId = requestAnimationFrame(draw);
      }}

      window.addEventListener('resize', restart, {{ passive: true }});
      if (reducedMotion.addEventListener) reducedMotion.addEventListener('change', restart);
      else if (reducedMotion.addListener) reducedMotion.addListener(restart);
      restart();
    }})();
  </script>
</body>
</html>
"""


def render_landing_page() -> None:
    import streamlit as st
    from streamlit.components.v1 import html as components_html

    st.markdown(
        """
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"], section.main {
          height: 100vh !important;
          max-height: 100vh !important;
          overflow: hidden !important;
        }
        .block-container { max-width: none !important; padding: 0 !important; margin: 0 !important; }
        iframe { display: block !important; }
        .parent-click-target {
          position: fixed !important; inset: 0 !important; z-index: 2147483647 !important;
          display: block !important; background: rgba(0,0,0,0) !important;
          cursor: pointer !important; text-decoration: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components_html(_build_landing_html(), height=900, scrolling=False)
    st.markdown(
        '<a class="parent-click-target" href="?view=app" target="_self" aria-label="Open vaccine prescription generator"></a>',
        unsafe_allow_html=True,
    )
    st.stop()
