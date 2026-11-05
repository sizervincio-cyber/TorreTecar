# Torre Tecar no VPS (Fase 1)

Sistema independente no VPS compartilhado com a Quântica e o RadarDispensa. A Torre não altera contêineres, bancos, volumes nem redes deles. O único ponto de contato é o **Caddy do RadarDispensa**, dono da porta 443: ele encaminha os nomes da Torre para `torre-api:8000` pela rede `proxy_edge`. O contêiner `radar` não participa dessa rede.

| Contêiner (projeto `torre`) | Função | Limites |
|---|---|---|
| `api` (alias `torre-api`) | Login, páginas protegidas, `/api/leads` | 256 MB · 0,5 CPU |
| `db` | Postgres 16 (rede interna, sem porta no host) | 256 MB · 0,5 CPU |
| `atualiza-dados` | `git pull` a cada 10 min (dados das rotinas do GitHub Actions) | 64 MB · 0,2 CPU |

Endereços provisórios: `https://torre.2-25-95-244.sslip.io` (painel) e `https://simule.2-25-95-244.sslip.io` (simulador público).

## Instalação

```bash
mkdir -p /opt/torre && git clone https://github.com/sizervincio-cyber/TorreTecar.git /opt/torre/repo
cd /opt/torre/repo/deploy && ./instalar.sh
docker compose exec api python -m server.app.cli criar --login SEU_LOGIN --perfil admin --nome "Seu Nome"
docker run --rm --network proxy_edge curlimages/curl -s http://torre-api:8000/api/health
```

## Publicação (rota no Caddy do RadarDispensa)

1. Merge do PR `zero-touch-ops#2` (bloco da Torre no Caddyfile + `caddy` na rede `proxy_edge`).
2. Em horário de pouco uso: `cd /opt/radardispensa/repo/product/radardispensa/vps && ./atualizar.sh`. O `caddy` do RadarDispensa é recriado (alguns segundos sem HTTPS para o RadarDispensa); o contêiner `radar` não.
3. Conferir: o RadarDispensa abre normalmente; `https://torre.2-25-95-244.sslip.io` pede login; `https://simule.2-25-95-244.sslip.io` abre o simulador.

## Usuários

```bash
cd /opt/torre/repo/deploy
docker compose exec api python -m server.app.cli listar
docker compose exec api python -m server.app.cli criar --login giselle.lima@tecar.com.br --perfil simulacao --nome "Giselle"
docker compose exec api python -m server.app.cli senha --login SEU_LOGIN
docker compose exec api python -m server.app.cli desativar --login ALGUEM
```

Perfis: `admin`, `gestor`, `vendedor` (painel completo por enquanto; a separação por carteira é a Fase 4) e `simulacao` (só simuladores; os arquivos de dados respondem 403).

## Rotina

- Atualizar o código: `./atualizar.sh`
- Backup diário (cron do root): `15 3 * * * /opt/torre/repo/deploy/backup.sh >> /var/log/torre-backup.log 2>&1`
- Logs: `docker compose logs --tail 80 api`

## Quando o repositório ficar privado

O `atualiza-dados` precisa de uma chave de deploy só de leitura:

```bash
ssh-keygen -t ed25519 -N "" -f /opt/torre/repo/deploy/ssh/id_ed25519 -C torre-vps
ssh-keyscan github.com > /opt/torre/repo/deploy/ssh/known_hosts
cat /opt/torre/repo/deploy/ssh/id_ed25519.pub   # GitHub > repositório > Settings > Deploy keys (sem escrita)
git -C /opt/torre/repo remote set-url origin git@github.com:sizervincio-cyber/TorreTecar.git
docker compose up -d atualiza-dados
```

## Desfazer

`docker compose down` (os dados ficam no volume `torre_pg`) e reverter o PR do `zero-touch-ops` com `./atualizar.sh` do RadarDispensa.
