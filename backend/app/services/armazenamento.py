"""Armazenamento de arquivos enviados (fotos das quadras) no disco local.

Os arquivos ficam em ``UPLOAD_DIR`` e são servidos pela própria API em ``/uploads/...``.
Isolado aqui para que trocar por um storage externo (S3 etc.) não afete os serviços.
"""

from pathlib import Path

from app.core.config import settings

URL_PREFIXO = "/uploads/"


def _raiz() -> Path:
    return Path(settings.upload_dir)


def salvar(conteudo: bytes, caminho_relativo: str) -> str:
    """Grava o arquivo e devolve a URL pública relativa (ex.: /uploads/quadras/1/x.jpg)."""
    destino = _raiz() / caminho_relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(conteudo)
    return URL_PREFIXO + caminho_relativo


def remover(url: str) -> None:
    if not url.startswith(URL_PREFIXO):
        return
    caminho = (_raiz() / url.removeprefix(URL_PREFIXO)).resolve()
    if _raiz().resolve() in caminho.parents:  # nunca apaga fora do diretório de uploads
        caminho.unlink(missing_ok=True)
