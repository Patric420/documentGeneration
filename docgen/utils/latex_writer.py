import logging
import subprocess
import os
from typing import Dict
from exceptions import LatexCompilationError, TemplateNotFoundError

logger = logging.getLogger(__name__)

def _sanitize_latex(text: str) -> str:
    """Sanitize user input to prevent LaTeX injection attacks."""
    if not text:
        return text
    
    # Escape special LaTeX characters using character-by-character replacement
    # to avoid corrupting already-substituted sequences.
    char_map = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    result = []
    for ch in text:
        result.append(char_map.get(ch, ch))
    sanitized = ''.join(result)
    
    logger.debug(f"Sanitized text (length: {len(text)} -> {len(sanitized)})")
    return sanitized

def populate_template(template_path: str, values: Dict[str, str]) -> str:
    """Load a LaTeX template and replace variables with sanitized values."""
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            tex = f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise TemplateNotFoundError(f"Template file not found: {template_path}")

    # Replace template fields with sanitized user values
    for k, v in values.items():
        placeholder = f"{{{{{k}}}}}"
        sanitized_value = _sanitize_latex(str(v))
        tex = tex.replace(placeholder, sanitized_value)
    
    return tex

def compile_latex(tex: str, output_tex: str, output_pdf: str) -> None:
    """Save LaTeX content to a file and compile it to PDF."""
    try:
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(tex)
        logger.debug(f"Written LaTeX file: {output_tex}")
    except IOError as e:
        logger.error(f"Failed to write LaTeX file: {str(e)}")
        raise

    logger.info(f"Compiling LaTeX to PDF: {output_pdf}")
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", output_tex],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"PDF successfully generated: {output_pdf}")
    except subprocess.CalledProcessError as e:
        logger.error(f"LaTeX compilation failed: {e.stderr}")
        raise LatexCompilationError(f"LaTeX compilation failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("pdflatex not found. Please install LaTeX distribution (e.g., MiKTeX, TeX Live)")
        raise LatexCompilationError("pdflatex not found. Install LaTeX distribution (MiKTeX, TeX Live, MacTeX, etc.)")

def render_latex(template_path: str, output_tex: str, output_pdf: str, values: Dict[str, str]) -> None:
    """
    Render a LaTeX template with user values and generate a PDF.
    
    Args:
        template_path: Path to LaTeX template file
        output_tex: Output path for rendered LaTeX file
        output_pdf: Output path for generated PDF
        values: Dictionary of field values to replace in template
        
    Raises:
        TemplateNotFoundError: If template file not found
        LatexCompilationError: If LaTeX compilation fails
    """
    logger.info(f"Rendering LaTeX template: {template_path}")
    tex = populate_template(template_path, values)
    compile_latex(tex, output_tex, output_pdf)
