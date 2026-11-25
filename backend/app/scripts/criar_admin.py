"""Cria (ou promove) um usuário administrador. Atalho para ``criar_usuario --papel administrador``.

Uso:
    python -m app.scripts.criar_admin --nome "Admin" --email admin@muzzi.local
    (a senha é pedida no terminal)
"""

from app.models import PapelUsuario
from app.scripts.criar_usuario import main

if __name__ == "__main__":
    main(papel_padrao=PapelUsuario.ADMINISTRADOR.value)
