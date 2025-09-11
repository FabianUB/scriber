from .document import Document as _Document


def document(output_path: str, size: str = "A4", margin: int = 32):
    return _Document(output_path=output_path, size=size, margin=margin)

