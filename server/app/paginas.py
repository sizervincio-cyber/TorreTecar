"""Tela de login (HTML próprio do servidor, sem dependências externas)."""
from __future__ import annotations

from html import escape

# Arte de abertura da Torre; servida sem sessão porque aparece antes do login (ver site.LOGIN_PUBLICO).
FUNDO = "/ASSETS/login-fundo.webp"

_LOGIN = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Entrar · Torre Tecar</title>
<link rel="preload" as="image" href="{fundo}">
<style>
:root{--bg:#060e17;--painel:#0a1520;--card:rgba(13,24,35,.88);--tx:#eef2f6;--mut:#93a1b1;--bd:#1f2e3d;
--laranja:#e47b2c;--laranja-2:#f29a4a;--err:#ff8a73}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--bg);color:var(--tx);
font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.palco{min-height:100vh;display:grid;grid-template-columns:minmax(0,1fr) 440px}
.arte{position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;background:var(--bg)}
.arte img{width:100%;height:100%;max-height:100vh;object-fit:contain;display:block}
.arte::after{content:"";position:absolute;inset:0 0 0 auto;width:120px;background:linear-gradient(90deg,transparent,var(--painel));pointer-events:none}
.lado{display:flex;align-items:center;justify-content:center;padding:32px;background:var(--painel);border-left:1px solid var(--bd)}
form{width:100%;max-width:360px;background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:30px;
box-shadow:0 24px 60px rgba(0,0,0,.45)}
.marca{display:flex;align-items:center;gap:10px;margin:0 0 6px}
.marca i{width:4px;height:26px;border-radius:2px;background:var(--laranja)}
h1{font-size:22px;letter-spacing:.2px;margin:0}
p.s{margin:0 0 24px;color:var(--mut);font-size:13px}
label{display:block;font-size:13px;font-weight:600;margin:16px 0 6px;color:#d7dee6}
input{width:100%;padding:12px 13px;border:1px solid var(--bd);border-radius:10px;background:rgba(4,12,19,.7);color:var(--tx);font:inherit}
input:focus{outline:2px solid var(--laranja);outline-offset:1px;border-color:transparent}
button{margin-top:24px;width:100%;padding:13px;border:0;border-radius:10px;background:linear-gradient(180deg,var(--laranja-2),var(--laranja));
color:#1a0d02;font:inherit;font-weight:800;letter-spacing:.3px;cursor:pointer}
button:hover{filter:brightness(1.06)}
button:focus-visible{outline:2px solid #fff;outline-offset:2px}
.err{color:var(--err);font-size:13px;margin:14px 0 0;min-height:1em}
.rodape{margin:18px 0 0;color:var(--mut);font-size:11.5px;text-align:center}
@media (max-width:900px){
 .palco{grid-template-columns:1fr;grid-template-rows:auto 1fr}
 .arte img{height:auto;max-height:none}
 .arte::after{inset:auto 0 0 0;width:auto;height:70px;background:linear-gradient(180deg,transparent,var(--painel))}
 .lado{border-left:0;padding:8px 16px 32px;align-items:flex-start}
}
</style></head><body>
<div class="palco">
<div class="arte"><img src="{fundo}" alt="Tecar Caminhões · Análise de Inteligência de Mercado · Mercedes-Benz"></div>
<div class="lado">
<form method="post" action="/login" autocomplete="on">
<div class="marca"><i></i><h1>Torre Tecar</h1></div><p class="s">Inteligência comercial · acesso restrito</p>
<input type="hidden" name="next" value="{next}">
<label for="login">Usuário</label><input id="login" name="login" autocomplete="username" required autofocus value="{login}">
<label for="senha">Senha</label><input id="senha" name="senha" type="password" autocomplete="current-password" required>
<p class="err" role="alert">{erro}</p>
<button type="submit">Entrar</button>
<p class="rodape">Acesso individual. Não compartilhe sua senha.</p>
</form>
</div>
</div></body></html>"""


def pagina_login(next_: str = "/", erro: str = "", login: str = "") -> str:
    return (_LOGIN.replace("{fundo}", FUNDO).replace("{next}", escape(next_)).replace("{erro}", escape(erro))
            .replace("{login}", escape(login)))
