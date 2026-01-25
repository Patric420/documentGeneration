import subprocess
import os

def render_latex(template_path, output_tex, output_pdf, values):
    with open(template_path, "r", encoding="utf-8") as f:
        tex = f.read()

    for k, v in values.items():
        tex = tex.replace(f"{{{{{k}}}}}", v)

    with open(output_tex, "w", encoding="utf-8") as f:
        f.write(tex)

    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", output_tex],
        check=True
    )
