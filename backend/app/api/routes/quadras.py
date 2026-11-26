from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status

from app.api.deps import DbSession, UsuarioAtual, UsuarioOpcional, exigir_papel
from app.core.config import settings
from app.models import PapelUsuario, TipoPiso, Usuario
from app.schemas.common import Pagina
from app.schemas.quadra import (
    FotoQuadraPublica,
    QuadraCriar,
    QuadraPublica,
    QuadraResumo,
    UploadFotosResposta,
)
from app.services import quadra_service
from app.services.quadra_service import ArquivoEnviado

router = APIRouter(prefix="/quadras", tags=["Quadras"])

DonoAtual = Annotated[Usuario, Depends(exigir_papel(PapelUsuario.DONO_QUADRA))]

_CHUNK = 64 * 1024

PaginaParam = Annotated[int, Query(ge=1, description="Página, a partir de 1")]
PorPaginaParam = Annotated[int, Query(ge=1, le=100, description="Itens por página (máx. 100)")]
CidadeParam = Annotated[
    str | None,
    Query(max_length=100, description="Parte do nome da cidade; todas as palavras devem constar"),
]


def _pagina(quadras, total: int, pagina: int, por_pagina: int) -> Pagina[QuadraResumo]:
    itens = [QuadraResumo.model_validate(q) for q in quadras]
    return Pagina[QuadraResumo].montar(itens, total, pagina, por_pagina)


@router.get("", response_model=Pagina[QuadraResumo], summary="Buscar quadras (público)")
def listar_quadras(
    db: DbSession,
    cidade: CidadeParam = None,
    tipo_piso: TipoPiso | None = None,
    coberta: bool | None = None,
    pagina: PaginaParam = 1,
    por_pagina: PorPaginaParam = 20,
) -> Pagina[QuadraResumo]:
    """Quadras ativas de donos ativos, ordenadas por nome. Não exige login."""
    quadras, total = quadra_service.listar_quadras(
        db,
        cidade=cidade,
        tipo_piso=tipo_piso,
        coberta=coberta,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    return _pagina(quadras, total, pagina, por_pagina)


@router.get(
    "/minhas",
    response_model=Pagina[QuadraResumo],
    summary="Quadras do dono autenticado (inclui inativas)",
)
def listar_minhas_quadras(
    db: DbSession,
    dono: DonoAtual,
    cidade: CidadeParam = None,
    tipo_piso: TipoPiso | None = None,
    coberta: bool | None = None,
    pagina: PaginaParam = 1,
    por_pagina: PorPaginaParam = 20,
) -> Pagina[QuadraResumo]:
    quadras, total = quadra_service.listar_quadras(
        db,
        dono_id=dono.id,
        cidade=cidade,
        tipo_piso=tipo_piso,
        coberta=coberta,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    return _pagina(quadras, total, pagina, por_pagina)


@router.get("/{quadra_id}", response_model=QuadraPublica, summary="Detalhes da quadra (público)")
def obter_quadra(quadra_id: int, db: DbSession, usuario: UsuarioOpcional) -> QuadraPublica:
    """Dados completos e todas as fotos. Quadra inativa só aparece para o dono e o
    administrador (envie o token); para os demais, ``404 QUADRA_NAO_ENCONTRADA``."""
    return QuadraPublica.model_validate(quadra_service.obter_quadra_visivel(db, quadra_id, usuario))


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
