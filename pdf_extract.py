# pdf_extract.py (versión mejorada)
from pypdf import PdfReader
from pathlib import Path
import re

def extract_text_from_pdf(path: Path) -> str:
    """Extrae texto limpio de un PDF. Si hay error o está vacío, devuelve string vacío."""
    try:
        reader = PdfReader(path)
        pages_text = []

        for p in reader.pages:
            text = p.extract_text() or ""
            # Limpieza básica
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                pages_text.append(text)

        full_text = "\n".join(pages_text)
        # Limpieza final
        full_text = re.sub(r"\n{2,}", "\n", full_text)
        return full_text.strip()

    except Exception as e:
        print(f"[ERROR] No se pudo leer PDF {path.name}: {e}")
        return ""

if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1])
    print(extract_text_from_pdf(p))
