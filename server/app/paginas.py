"""Tela de login (HTML próprio do servidor, sem dependências externas)."""
from __future__ import annotations

from html import escape

# Arte de abertura da Torre; servida sem sessão porque aparece antes do login (ver site.recurso_do_login).
FUNDO = "/ASSETS/login-fundo.webp"

_ICONE_USUARIO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/>'
                  '<path d="M4 20c1.6-3.6 4.6-5 8-5s6.4 1.4 8 5"/></svg>')
_ICONE_CADEADO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/>'
                  '<path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>')
_ICONE_OLHO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/>'
               '<circle cx="12" cy="12" r="3"/><path class="risco" d="M4 4l16 16"/></svg>')
_ICONE_SETA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

_LOGIN = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Entrar · Torre Tecar</title>
<link rel="preload" as="image" href="{fundo}">
<style>
:root{--bg:#030c15;--tx:#f1f4f8;--mut:#9aa8b8;--bd:#2a3846;--laranja:#f28c28;--laranja-2:#f7a53f;--err:#ff8a73}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--bg);color:var(--tx);
font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.palco{position:relative;min-height:100vh;display:flex;align-items:flex-start;justify-content:flex-end;
padding:clamp(24px,17.5vh,190px) clamp(16px,2.4vw,44px) 24px;overflow:hidden}
.arte{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:24% center;z-index:0}
.palco::after{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;
background:linear-gradient(90deg,transparent 58%,rgba(2,9,16,.55) 100%)}
form{position:relative;z-index:1;width:clamp(340px,22vw,400px);padding:38px 30px 30px;border-radius:18px;
background:rgba(9,17,26,.78);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
border:1px solid rgba(242,140,40,.6);
box-shadow:0 0 0 1px rgba(242,140,40,.12),0 0 32px rgba(242,140,40,.28),0 30px 70px rgba(0,0,0,.55)}
.marca{display:flex;align-items:center;gap:12px;margin:0 0 8px}
.marca i{width:4px;height:30px;border-radius:2px;background:var(--laranja)}
h1{font-size:29px;line-height:1.1;margin:0;font-weight:800;letter-spacing:.2px}
p.s{margin:0 0 30px;color:var(--mut);font-size:14px}
label{display:block;font-size:14px;font-weight:700;margin:18px 0 8px}
.campo{position:relative}
.campo>svg,.olho svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.campo>svg{position:absolute;left:15px;top:50%;transform:translateY(-50%);color:#c9d2dc;pointer-events:none}
input{width:100%;height:50px;padding:0 46px 0 46px;border:1px solid var(--bd);border-radius:11px;
background:rgba(2,9,16,.66);color:var(--tx);font:inherit}
input:focus{outline:none;border-color:var(--laranja);box-shadow:0 0 0 3px rgba(242,140,40,.22),0 0 18px rgba(242,140,40,.18)}
.olho{position:absolute;right:8px;top:50%;transform:translateY(-50%);width:36px;height:36px;display:grid;place-items:center;
border:0;border-radius:8px;background:transparent;color:#c9d2dc;cursor:pointer;padding:0}
.olho:hover{color:#fff}.olho:focus-visible{outline:2px solid var(--laranja)}
.olho[aria-pressed="true"] .risco{display:none}
.err{color:var(--err);font-size:13px;margin:14px 0 0;min-height:1em}
button.entrar{margin-top:16px;width:100%;height:52px;border:0;border-radius:11px;cursor:pointer;
display:flex;align-items:center;justify-content:center;gap:10px;
background:linear-gradient(180deg,var(--laranja-2),var(--laranja));color:#0d1620;font:inherit;font-size:18px;font-weight:800;
box-shadow:0 10px 26px rgba(242,140,40,.28)}
button.entrar svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
button.entrar:hover{filter:brightness(1.06)}button.entrar:focus-visible{outline:2px solid #fff;outline-offset:2px}
.rodape{display:flex;align-items:center;justify-content:center;gap:8px;margin:20px 0 0;color:var(--mut);font-size:12.5px}
.rodape svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
@media (max-width:999px){
 .palco{flex-direction:column;justify-content:flex-start;align-items:center;padding:0 0 32px;min-height:100vh}
 .palco::after{display:none}
 .arte{position:static;height:auto;aspect-ratio:1672/941;object-fit:cover;object-position:center}
 form{width:min(420px,calc(100% - 32px));margin-top:-28px}
}
</style></head><body>
<main class="palco">
<img class="arte" src="{fundo}" alt="Tecar Caminhões · Análise de Inteligência de Mercado · Mercedes-Benz">
<form method="post" action="/login" autocomplete="on">
<div class="marca"><i></i><h1>Torre Tecar</h1></div><p class="s">Inteligência comercial · Acesso restrito</p>
<input type="hidden" name="next" value="{next}">
<label for="login">Usuário</label>
<div class="campo">{icone_usuario}<input id="login" name="login" autocomplete="username" required autofocus value="{login}"></div>
<label for="senha">Senha</label>
<div class="campo">{icone_cadeado}<input id="senha" name="senha" type="password" autocomplete="current-password" required>
<button type="button" class="olho" aria-label="Mostrar senha" aria-pressed="false">{icone_olho}</button></div>
<p class="err" role="alert">{erro}</p>
<button type="submit" class="entrar">Entrar {icone_seta}</button>
<p class="rodape">{icone_cadeado}Acesso individual. Não compartilhe sua senha.</p>
</form>
</main>
<script>
document.querySelector('.olho').addEventListener('click',function(){
  var s=document.getElementById('senha'),ver=s.type==='password';
  s.type=ver?'text':'password';this.setAttribute('aria-pressed',String(ver));
  this.setAttribute('aria-label',ver?'Ocultar senha':'Mostrar senha');s.focus();
});
</script>
</body></html>"""


def pagina_login(next_: str = "/", erro: str = "", login: str = "") -> str:
    return (_LOGIN.replace("{fundo}", FUNDO).replace("{icone_usuario}", _ICONE_USUARIO)
            .replace("{icone_cadeado}", _ICONE_CADEADO).replace("{icone_olho}", _ICONE_OLHO)
            .replace("{icone_seta}", _ICONE_SETA)
            .replace("{next}", escape(next_)).replace("{erro}", escape(erro)).replace("{login}", escape(login)))
