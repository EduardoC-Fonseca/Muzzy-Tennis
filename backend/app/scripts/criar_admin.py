"""Cria (ou promove) um usuário administrador.

Uso:
    python -m app.scripts.criar_admin --nome "Admin" --email admin@muzzi.local
    (a senha é pedida no terminal)
"""

import argparse
import getpass

from sqlalchemy import select

from app.core.security import hash_senha
from app.db.session import SessionLocal
from app.models import PapelUsuario, Usuario


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    senha = getpass.getpass("Senha: ")
    if len(senha) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")

    email = args.email.strip().lower()
    with SessionLocal() as db:
        usuario = db.scalar(select(Usuario).where(Usuario.email == email))
        if usuario is None:
            usuario = Usuario(nome=args.nome, email=email)
            db.add(usuario)
        usuario.senha_hash = hash_senha(senha)
        usuario.papel = PapelUsuario.ADMINISTRADOR
        usuario.status = True
        db.commit()
        print(f"Administrador pronto: {usuario.email} (id={usuario.id})")


if __name__ == "__main__":
    main()
