"""The content blocks of a claim's documents, as built in Lab 2."""
import base64
from pathlib import Path

CLAIMS = Path(__file__).resolve().parent.parent / "data" / "claims"


def image_block(path: Path) -> dict:
    """The attendance scan as an image content block."""
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return {"type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": data}}


def pdf_block(path: Path) -> dict:
    """The invoice as a document content block."""
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return {"type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": data}}


def claim_blocks(claim: str) -> list:
    """The attendance list, then the invoice, of one claim."""
    folder = CLAIMS / claim
    return [image_block(folder / "attendance.jpg"), pdf_block(folder / "invoice.pdf")]


def all_claims() -> list:
    """Every claim number in the data folder, in order."""
    return sorted(p.name for p in CLAIMS.iterdir() if p.is_dir())
