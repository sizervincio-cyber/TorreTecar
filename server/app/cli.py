"""Administração de usuários pela linha de comando (no contêiner da API).

  python -m server.app.cli criar --login matheus --perfil admin --nome "Matheus"
  python -m server.app.cli senha --login matheus
  python -m server.app.cli desativar --login giselle
  python -m server.app.cli listar

A senha é pedida no terminal (ou lida da entrada com --senha-stdin) e nunca aparece no histórico do shell.
"""
from __future__ import annotations

import argparse
import getpass
import sys

from sqlalchemy import select

from .auth import encerra_sessoes_do_usuario, hash_senha
from .config import PERFIS, load_settings
from .db import make_engine, make_sessionmaker
from .models import Usuario


def _senha(a) -> str:
    if a.senha_stdin:
        return sys.stdin.readline().rstrip("\n")
    s1 = getpass.getpass("Senha (mín. 10 caracteres): ")
    if s1 != getpass.getpass("Repita a senha: "):
        raise SystemExit("As senhas não conferem.")
    return s1


def main(argv=None, engine=None) -> int:
    p = argparse.ArgumentParser(prog="torre-usuarios")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("criar")
    c.add_argument("--login", required=True)
    c.add_argument("--perfil", required=True, choices=PERFIS)
    c.add_argument("--nome", default="")
    c.add_argument("--senha-stdin", action="store_true")
    s = sub.add_parser("senha")
    s.add_argument("--login", required=True)
    s.add_argument("--senha-stdin", action="store_true")
    d = sub.add_parser("desativar")
    d.add_argument("--login", required=True)
    pf = sub.add_parser("perfil")
    pf.add_argument("--login", required=True)
    pf.add_argument("--perfil", required=True, choices=PERFIS)
    sub.add_parser("listar")
    a = p.parse_args(argv)

    Sessions = make_sessionmaker(engine or make_engine(load_settings().database_url))
    with Sessions() as db:
        login = getattr(a, "login", "").strip().lower()
        u = db.scalar(select(Usuario).where(Usuario.login == login)) if login else None
        if a.cmd == "listar":
            for x in db.scalars(select(Usuario).order_by(Usuario.login)):
                print(f"{x.login:32} {x.perfil:10} {'ativo' if x.ativo else 'inativo':8} {x.nome}")
            return 0
        if a.cmd == "criar":
            if u is not None:
                raise SystemExit(f"O usuário {login} já existe.")
            db.add(Usuario(login=login, nome=a.nome, perfil=a.perfil, senha_hash=hash_senha(_senha(a))))
        elif u is None:
            raise SystemExit(f"Usuário {login} não encontrado.")
        elif a.cmd == "senha":
            u.senha_hash, u.ativo = hash_senha(_senha(a)), True
            encerra_sessoes_do_usuario(db, u.id)
        elif a.cmd == "desativar":
            u.ativo = False
            encerra_sessoes_do_usuario(db, u.id)
        elif a.cmd == "perfil":
            u.perfil = a.perfil
            encerra_sessoes_do_usuario(db, u.id)
        db.commit()
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
