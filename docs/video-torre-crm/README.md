# Vídeo comercial: Torre CRM

`torre-crm-comercial.mp4` · 1920×1080 · 30 fps · ~2min09 · narração pt-BR + trilha + legendas embutidas.

## Roteiro (10 cenas)
1. Gancho: vendedor digitando no CRM à noite
2. Problema: a venda acontece no WhatsApp, telefone e pátio, ~10% chega ao sistema
3. Revelação: Torre CRM, o CRM que se preenche sozinho
4. C · Captura: WhatsApp, ligações, agenda/e-mail, nota de voz → eventos com fonte
5. O · Organização: mapa de contexto (conta, contatos, frota, proposta, oportunidade)
6. R · Raciocínio: agentes (prep, pós-contato, deal parado, licitações, renovação de frota)
7. E · Execução: aprovação no celular, funil em tempo real, sync com o portal da montadora
8. Stack: FastAPI + Postgres/pgvector, Redis + Arq, Claude roteado, WhatsApp Cloud API + Whisper, Next.js, VPS/LGPD
9. Plano: piloto em 6 semanas
10. CTA

## Como regerar
```bash
cd fonte
# 1) narração (Piper TTS, voz pt-br-edresson-low)
i=0; while IFS= read -r l; do echo "$l" | piper -m pt-br-edresson-low.onnx --length_scale 1.05 --sentence_silence 0.35 -f raw_$i.wav; i=$((i+1)); done < narr.txt
python3 timing.py      # tempos de cena e legendas a partir da duração dos áudios
node preview.js        # quadros de conferência
node render.js         # renderiza scenes.html quadro a quadro → video_mudo.mp4
# 3) mixagem de voz + trilha e mux final: ver comandos ffmpeg no histórico do projeto
```
Para trocar a voz por uma voz premium (ElevenLabs, Higgsfield etc.), basta substituir os `raw_N.wav` e rodar de novo a partir do `timing.py`: o vídeo se reajusta sozinho à nova duração.
