"""Cadastro de quadras e fotos (tarefa 12 — HU03, CT07–CT10) e consulta (tarefa 13)."""

import uuid
from dataclasses import dataclass

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import AcessoNegadoError, NaoEncontradoError, RegraNegocioError
from app.models import FotoQuadra, PapelUsuario, Quadra, TipoPiso, Usuario
from app.schemas.quadra import FotoRejeitada, QuadraCriar
from app.services import armazenamento

# Tipos aceitos, identificados pelo conteúdo do arquivo (assinatura), não pela extensão
# nem pelo Content-Type informado pelo navegador.
TIPOS_SUPORTADOS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def detectar_tipo_imagem(cabecalho: bytes) -> str | None:
    if cabecalho.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if cabecalho.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if cabecalho[:4] == b"RIFF" and cabecalho[8:12] == b"WEBP":
        return "image/webp"
    return None


@dataclass
class ArquivoEnviado:
    nome: str
    conteudo: bytes
    excedeu_tamanho: bool = False


def criar_quadra(db: Session, dono: Usuario, dados: QuadraCriar) -> Quadra:
    quadra = Quadra(dono_id=dono.id, **dados.model_dump())
    db.add(quadra)
    db.commit()
    return obter_quadra(db, quadra.id)


def obter_quadra(db: Session, quadra_id: int) -> Quadra:
    quadra = db.scalar(
        select(Quadra).where(Quadra.id == quadra_id).options(selectinload(Quadra.fotos))
    )
    if quadra is None:
        raise NaoEncontradoError("Quadra não encontrada.", code="QUADRA_NAO_ENCONTRADA")
    return quadra


def obter_quadra_para_gerenciar(db: Session, quadra_id: int, usuario: Usuario) -> Quadra:
    """Quadra que o usuário pode alterar: o dono dela ou um administrador."""
    quadra = obter_quadra(db, quadra_id)
    if usuario.papel != PapelUsuario.ADMINISTRADOR and quadra.dono_id != usuario.id:
        raise AcessoNegadoError("Você não pode alterar uma quadra de outro proprietário.")
    return quadra


def _rejeitar(nome: str, code: str, motivo: str) -> FotoRejeitada:
    return FotoRejeitada(nome_arquivo=nome, code=code, motivo=motivo)


def adicionar_fotos(
    db: Session, quadra: Quadra, arquivos: list[ArquivoEnviado]
) -> tuple[list[FotoQuadra], list[FotoRejeitada]]:
    """Valida e grava as fotos (CT09). Fotos válidas são salvas mesmo que outras sejam
    rejeitadas; cada rejeição volta com o motivo. Se nenhuma for aceita, lança erro 422."""
    limite_mb = settings.upload_max_bytes / (1024 * 1024)
    existentes = db.scalar(select(func.count()).where(FotoQuadra.quadra_id == quadra.id)) or 0
    proxima_ordem = (
        db.scalar(select(func.max(FotoQuadra.ordem)).where(FotoQuadra.quadra_id == quadra.id)) or 0
    ) + (1 if existentes else 0)
    vagas = settings.fotos_max_por_quadra - existentes

    aceitas: list[FotoQuadra] = []
    rejeitadas: list[FotoRejeitada] = []
    gravadas: list[str] = []

    for arquivo in arquivos:
        if arquivo.excedeu_tamanho:
            rejeitadas.append(
                _rejeitar(
                    arquivo.nome,
                    "ARQUIVO_MUITO_GRANDE",
                    f"O arquivo excede o tamanho máximo de {limite_mb:g} MB.",
                )
            )
            continue
        if not arquivo.conteudo:
            rejeitadas.append(_rejeitar(arquivo.nome, "ARQUIVO_VAZIO", "O arquivo está vazio."))
            continue
        tipo = detectar_tipo_imagem(arquivo.conteudo[:16])
        if tipo is None:
            rejeitadas.append(
                _rejeitar(
                    arquivo.nome,
                    "TIPO_NAO_SUPORTADO",
                    "Tipo de arquivo não suportado. Envie imagens JPEG, PNG ou WebP.",
                )
            )
            continue
        if len(aceitas) >= vagas:
            rejeitadas.append(
                _rejeitar(
                    arquivo.nome,
                    "LIMITE_FOTOS",
                    f"A quadra já atingiu o limite de {settings.fotos_max_por_quadra} fotos.",
                )
            )
            continue

        caminho = f"quadras/{quadra.id}/{uuid.uuid4().hex}.{TIPOS_SUPORTADOS[tipo]}"
        url = armazenamento.salvar(arquivo.conteudo, caminho)
        gravadas.append(url)
        aceitas.append(
            FotoQuadra(
                quadra_id=quadra.id,
                url=url,
                nome_arquivo=arquivo.nome[:255],
                tipo_arquivo=tipo,
                tamanho_bytes=len(arquivo.conteudo),
                principal=existentes == 0 and not aceitas,  # 1ª foto da quadra é a principal
                ordem=proxima_ordem + len(aceitas),
            )
        )

    if not aceitas:
        raise RegraNegocioError(
            "Nenhuma foto foi aceita.",
            code="FOTOS_REJEITADAS",
            extra={"rejeitadas": [r.model_dump() for r in rejeitadas]},
        )

    try:
        db.add_all(aceitas)
        db.commit()
    except Exception:
        db.rollback()
        for url in gravadas:  # não deixa arquivos órfãos no disco
            armazenamento.remover(url)
        raise
    return aceitas, rejeitadas


def remover_foto(db: Session, quadra: Quadra, foto_id: int) -> None:
    foto = db.get(FotoQuadra, foto_id)
    if foto is None or foto.quadra_id != quadra.id:
        raise NaoEncontradoError("Foto não encontrada.", code="FOTO_NAO_ENCONTRADA")
    era_principal = foto.principal
    url = foto.url
    db.delete(foto)
    db.flush()
    if era_principal:  # promove a próxima foto (menor ordem) a principal
        proxima = db.scalar(
            select(FotoQuadra)
            .where(FotoQuadra.quadra_id == quadra.id)
            .order_by(FotoQuadra.ordem, FotoQuadra.id)
            .limit(1)
        )
        if proxima is not None:
            proxima.principal = True
    db.commit()
    armazenamento.remover(url)


# --- Consulta (tarefa 13) ----------------------------------------------------------------


def _escapar_like(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _visivel_ao_publico():
    """Quadra ativa de dono ativo: o que clientes (sem login) podem ver."""
    return and_(Quadra.ativa.is_(True), Usuario.status.is_(True))


def listar_quadras(
    db: Session,
    *,
    pagina: int,
    por_pagina: int,
    cidade: str | None = None,
    tipo_piso: TipoPiso | None = None,
    coberta: bool | None = None,
    dono_id: int | None = None,
) -> tuple[list[Quadra], int]:
    """Busca paginada, ordenada por nome.

    Sem ``dono_id``: só quadras visíveis ao público. Com ``dono_id``: todas as quadras do dono,
    inclusive inativas. ``cidade`` casa por palavras (todas precisam aparecer), sem diferenciar
    maiúsculas; no MySQL também ignora acentos (collation ``utf8mb4_0900_ai_ci``).
    """
    filtros = []
    if dono_id is None:
        filtros.append(_visivel_ao_publico())
    else:
        filtros.append(Quadra.dono_id == dono_id)
    for palavra in (cidade or "").split():
        filtros.append(Quadra.cidade.ilike(f"%{_escapar_like(palavra)}%", escape="\\"))
    if tipo_piso is not None:
        filtros.append(Quadra.tipo_piso == tipo_piso)
    if coberta is not None:
        filtros.append(Quadra.coberta.is_(coberta))

    base = select(Quadra).join(Quadra.dono).where(*filtros)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    quadras = db.scalars(
        base.options(selectinload(Quadra.fotos))
        .order_by(Quadra.nome, Quadra.id)
        .limit(por_pagina)
        .offset((pagina - 1) * por_pagina)
    ).all()
    return list(quadras), total


def obter_quadra_visivel(db: Session, quadra_id: int, usuario: Usuario | None) -> Quadra:
    """Detalhe da quadra. Inativa (ou de dono inativo) só aparece para o dono e o administrador;
    para os demais responde 404, como se não existisse."""
    quadra = obter_quadra(db, quadra_id)
    visivel = quadra.ativa and quadra.dono.ativo
    pode_gerenciar = usuario is not None and (
        usuario.papel == PapelUsuario.ADMINISTRADOR or usuario.id == quadra.dono_id
    )
    if not (visivel or pode_gerenciar):
        raise NaoEncontradoError("Quadra não encontrada.", code="QUADRA_NAO_ENCONTRADA")
    return quadra
