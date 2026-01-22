from pathlib import Path
from typing import List

from app.models.documents import Document


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents_from_folder(folder_path: str) -> List[Document]:
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder not found or not a directory: {folder_path}")

    docs: List[Document] = []
    for file_path in sorted(folder.iterdir()):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        docs.append(
            Document(
                doc_id=file_path.stem,
                text=text,
                metadata={"source_file": file_path.name},
            )
        )

    return docs