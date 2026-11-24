from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from app.api.deps import DbSession, UsuarioAtual, exigir_papel
from app.core.config import settings
from app.models import PapelUsuario, Usuario
from app.schemas.quadra import FotoQuadraPublica, QuadraCriar, QuadraPublica, UploadFotosResposta
from app.services import quadra_service
from app.services.quadra_service import ArquivoEnviado

router = APIRouter(prefix="/quadras", tags=["Quadras"])

DonoAtual = Annotated[Usuario, Depends(exigir_papel(PapelUsuario.DONO_QUADRA))]

_CHUNK = 64 * 1024


async def _ler_limitado(arquivo: UploadFile) -> ArquivoEnviado:
    """Lê o arquivo até o limite configurado, sem carregar arquivos gigantes na memória."""
    partes, total = [], 0
    while chunk := await arquivo.read(_CHUNK):
        total += len(chunk)
        if total > settings.upload_max_bytes:
            return ArquivoEnviado(
                nome=arquivo.filename or "arquivo", conteudo=b"", excedeu_tamanho=True
            )
        partes.append(chunk)
    return ArquivoEnviado(nome=arquivo.filename or "arquivo", conteudo=b"".join(partes))


@router.post(
    "",
    response_model=QuadraPublica,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar quadra (dono de quadra)",
)
def criar_quadra(dados: QuadraCriar, db: DbSession, dono: DonoAtual) -> QuadraPublica:
    """Cria a quadra do proprietário autenticado. As fotos são enviadas em seguida, em
    ``POST /quadras/{id}/fotos``."""
    return QuadraPublica.model_validate(quadra_service.criar_quadra(db, dono, dados))


@router.post(
    "/{quadra_id}/fotos",
    response_model=UploadFotosResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar fotos da quadra (dono da quadra ou administrador)",
)
async def enviar_fotos(
    quadra_id: int,
    db: DbSession,
    usuario: UsuarioAtual,
    fotos: Annotated[list[UploadFile], File(description="Imagens JPEG, PNG ou WebP")],
) -> UploadFotosResposta:
    """Fotos válidas são salvas; as inválidas voltam em ``rejeitadas`` com o motivo (CT09).
    Se nenhuma for aceita, responde 422 com ``code = FOTOS_REJEITADAS``."""
    quadra = quadra_service.obter_quadra_para_gerenciar(db, quadra_id, usuario)
    arquivos = [await _ler_limitado(f) for f in fotos]
    aceitas, rejeitadas = quadra_service.adicionar_fotos(db, quadra, arquivos)
    return UploadFotosResposta(
        fotos=[FotoQuadraPublica.model_validate(f) for f in aceitas], rejeitadas=rejeitadas
    )


@router.delete(
    "/{quadra_id}/fotos/{foto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover foto da quadra (dono da quadra ou administrador)",
)
def remover_foto(quadra_id: int, foto_id: int, db: DbSession, usuario: UsuarioAtual) -> Response:
    quadra = quadra_service.obter_quadra_para_gerenciar(db, quadra_id, usuario)
    quadra_service.remover_foto(db, quadra, foto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
