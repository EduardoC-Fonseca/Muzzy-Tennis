"""Cria (ou atualiza) um usuário com senha — útil para testes manuais e para o primeiro acesso.

Uso:
    python -m app.scripts.criar_usuario --papel dono_quadra --nome "Dono" --email dono@muzzi.local
    python -m app.scripts.criar_usuario --papel administrador --nome "Admin" \
        --email admin@muzzi.local

A senha é pedida no terminal (ou lida de MUZZI_SENHA, para automação).
Se o e-mail já existir, o usuário é atualizado: nova senha, papel informado e conta ativa.
"""

import argparse
import getpass
import os

from sqlalchemy import select

from app.core.security import hash_senha
from app.db.session import SessionLocal
from app.models import PapelUsuario, Usuario

PAPEIS_COM_LOGIN = [PapelUsuario.DONO_QUADRA.value, PapelUsuario.ADMINISTRADOR.value]


def criar_ou_atualizar(nome: str, email: str, senha: str, papel: PapelUsuario) -> Usuario:
    if len(senha) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")
    email = email.strip().lower()
    with SessionLocal() as db:
        usuario = db.scalar(select(Usuario).where(Usuario.email == email))
        if usuario is None:
            usuario = Usuario(nome=nome, email=email)
            db.add(usuario)
        usuario.senha_hash = hash_senha(senha)
        usuario.papel = papel
        usuario.status = True
        usuario.data_desativacao = None
        db.commit()
        return usuario


def main(papel_padrao: str | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papel", choices=PAPEIS_COM_LOGIN, default=papel_padrao,
                        required=papel_padrao is None)  # fmt: skip
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    senha = os.environ.get("MUZZI_SENHA") or getpass.getpass("Senha: ")
    usuario = criar_ou_atualizar(args.nome, args.email, senha, PapelUsuario(args.papel))
    print(f"Usuário pronto: {usuario.email} (id={usuario.id}, papel={usuario.papel.value})")


if __name__ == "__main__":
    main()
