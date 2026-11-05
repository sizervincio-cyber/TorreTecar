"""Tela de login (HTML próprio do servidor, sem dependências externas)."""
from __future__ import annotations

from html import escape

_LOGIN = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entrar · Torre Tecar</title>
<style>
:root{--bg:#f4f5f7;--card:#fff;--tx:#111318;--mut:#667085;--bd:#d0d5dd;--pri:#111318;--err:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#0d0f13;--card:#171a21;--tx:#eef0f3;--mut:#98a2b3;--bd:#2d333d;--pri:#eef0f3;--err:#f97066}}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--tx);
font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:16px}
form{width:100%;max-width:360px;background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:28px}
h1{font-size:20px;margin:0 0 4px}p.s{margin:0 0 22px;color:var(--mut);font-size:13px}
label{display:block;font-size:13px;font-weight:600;margin:14px 0 6px}
input{width:100%;padding:11px 12px;border:1px solid var(--bd);border-radius:9px;background:transparent;color:var(--tx);font:inherit}
input:focus{outline:2px solid var(--pri);outline-offset:1px}
button{margin-top:22px;width:100%;padding:12px;border:0;border-radius:9px;background:var(--pri);color:var(--bg);font:inherit;font-weight:700;cursor:pointer}
.err{color:var(--err);font-size:13px;margin:14px 0 0;min-height:1em}
</style></head><body>
<form method="post" action="/login" autocomplete="on">
<h1>Torre Tecar</h1><p class="s">Inteligência comercial · acesso restrito</p>
<input type="hidden" name="next" value="{next}">
<label for="login">Usuário</label><input id="login" name="login" autocomplete="username" required autofocus value="{login}">
<label for="senha">Senha</label><input id="senha" name="senha" type="password" autocomplete="current-password" required>
<p class="err" role="alert">{erro}</p>
<button type="submit">Entrar</button>
</form></body></html>"""


def pagina_login(next_: str = "/", erro: str = "", login: str = "") -> str:
    return (_LOGIN.replace("{next}", escape(next_)).replace("{erro}", escape(erro))
            .replace("{login}", escape(login)))
