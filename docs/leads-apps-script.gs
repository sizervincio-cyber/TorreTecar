/**
 * Tecar · Leads do Simulador de TCO (simule.html)
 * Web App do Google Apps Script que grava cada lead em uma planilha e devolve a lista para o Torre.
 *
 * COMO INSTALAR (5 minutos)
 * 1. Crie uma planilha no Google Sheets (ex.: "Leads Simulador TCO").
 * 2. Extensões → Apps Script. Apague o conteúdo e cole este arquivo inteiro. Salve.
 * 3. Troque TOKEN abaixo por uma senha sua (letras e números).
 * 4. Implantar → Nova implantação → tipo "App da Web" → Executar como: "Eu" · Quem pode acessar: "Qualquer pessoa". Implantar e autorizar.
 * 5. Copie a "URL do app da Web" (termina em /exec). Ela vai em:
 *      - simule.html  →  CONFIG.LEAD_ENDPOINT = 'URL'
 *      - Analitycmbb.html → const LEADS_ENDPOINT = 'URL?token=SEU_TOKEN'
 * 6. Para atualizar o script depois: Implantar → Gerenciar implantações → editar → Nova versão.
 */
var TOKEN = 'troque-por-uma-senha';
var SHEET = 'Leads';
var COLS = ['quando', 'codigo', 'nome', 'telefone', 'email', 'empresa', 'lgpd', 'autoriza_contato', 'mb', 'concorrente', 'km_mes', 'horizonte', 'diesel', 'compra', 'preco_conc', 'kml_conc', 'tco_mb', 'tco_conc', 'km_mb', 'km_conc', 'economia', 'economia_pct', 'ua', 'json'];

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  if (sh.getLastRow() === 0) { sh.appendRow(COLS); sh.setFrozenRows(1); }
  return sh;
}
/* POST: recebe o lead em JSON (enviado pelo simule.html com mode no-cors) */
function doPost(e) {
  try {
    var p = JSON.parse(e.postData.contents || '{}');
    var op = (p.premissas && p.premissas.operacao) || {}, C = (p.premissas && p.premissas.C) || {}, r = p.resultado || {};
    sheet_().appendRow([p.quando || new Date().toISOString(), p.codigo || '', p.nome || '', p.telefone || '', p.email || '', p.empresa || '',
      p.lgpd ? 'Sim' : 'Não', p.autoriza_contato ? 'Sim' : 'Não', p.mb || '', p.concorrente || '', op.km || '', op.horiz || '', op.diesel || '',
      op.pag === 'fin' ? ('financiada ' + (op.entrada || 0) + '% / ' + (op.prazo || '') + 'm') : 'à vista', C.preco || '', C.kml || '',
      r.tco_mb || '', r.tco_conc || '', r.km_mb || '', r.km_conc || '', r.economia || '', r.economia_pct || '', p.ua || '', JSON.stringify(p)]);
    return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, erro: String(err) })).setMimeType(ContentService.MimeType.JSON);
  }
}
/* GET ?list=1&token=...: devolve os leads (JSON completo de cada linha) para a página Leads do Torre */
function doGet(e) {
  var q = (e && e.parameter) || {};
  if (q.token !== TOKEN) return ContentService.createTextOutput(JSON.stringify({ erro: 'token inválido' })).setMimeType(ContentService.MimeType.JSON);
  var sh = sheet_(), rows = sh.getDataRange().getValues(), head = rows.shift(), ij = head.indexOf('json');
  var out = rows.filter(function (r) { return r[ij]; }).map(function (r) { try { return JSON.parse(r[ij]); } catch (x) { return null; } }).filter(Boolean);
  return ContentService.createTextOutput(JSON.stringify({ leads: out })).setMimeType(ContentService.MimeType.JSON);
}
