/* Truck Test 2.0 · modelo de dados, cálculos e motor de TCO (mesma metodologia do tco-simulador.html). */
'use strict';
const TT = (() => {
const uid = () => 'tt' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const DRV_CRIT = [
 ['conforto', 'Conforto', 1.0], ['ergonomia', 'Ergonomia', 0.8], ['dirigibilidade', 'Dirigibilidade', 1.0], ['visibilidade', 'Visibilidade', 0.8],
 ['frenagem', 'Frenagem', 1.2], ['retomada', 'Retomada', 1.0], ['cambio', 'Câmbio', 1.0], ['manobra', 'Manobrabilidade', 0.8],
 ['ruido', 'Ruído', 0.8], ['fadiga', 'Fadiga', 1.2], ['seguranca', 'Percepção de segurança', 1.2]];
const COMPAT_ITEMS = [['modelo', 'Modelo'], ['motor', 'Motor'], ['potencia', 'Potência (cv)'], ['torque', 'Torque (Nm)'], ['transmissao', 'Transmissão'],
 ['relacao', 'Relação de diferencial'], ['entreEixos', 'Entre-eixos (mm)'], ['pneus', 'Pneus'], ['pbt', 'PBT (t)'], ['cmt', 'CMT (t)'],
 ['implemento', 'Implemento'], ['tecnologias', 'Tecnologias'], ['manutPlano', 'Pacote de manutenção']];
const NEW = () => ({
 id: uid(), criadoEm: new Date().toISOString(), atualizadoEm: new Date().toISOString(), nome: 'Novo Truck Test',
 cli: { empresa: '', cnpj: '', cidade: '', uf: '', segmento: '', atividade: '', logo: '', contato: '', cargo: '', vendedor: '', instrutor: '', frotaTotal: '', frotaElegivel: '', idadeMedia: '', marcas: '', dores: '' },
 op: { aplicacao: '', rotas: '', cargaMedia: '', cargaMax: '', implemento: '', kmMes: '', mixCarregado: 50, entregasDia: '', velMedia: '', perfilRod: '', ganhoAlt: '', paradas100: '', jornada: '', sazonalidade: '', diasOper: 25 },
 base: { marca: '', modelo: '', ano: '', qtd: '', kml: '', fonteKml: 'frota', arla: 6, manut: '', pneus: '', disp: '', diasParados: '', custoDiaParado: '', diesel: '', arlaPreco: 3.5, precoNovo: '', taxa: '', deprec: 10, residualPct: '' },
 vt: { modelo: '', placa: '', chassi: '', motor: '', potencia: '', torque: '', transmissao: '', relacao: '', entreEixos: '', pneus: '', pbt: '', cmt: '', implemento: '', tecnologias: '', manutPlano: '' },
 vo: { modelo: '', motor: '', potencia: '', torque: '', transmissao: '', relacao: '', entreEixos: '', pneus: '', pbt: '', cmt: '', implemento: '', tecnologias: '', manutPlano: '', preco: '' },
 compat: {}, features: '',
 prot: { inicio: '', fim: '', motorista: '', pctCliente: 90, metodo: 'ambos', clima: '', trafego: '', pressao: '', mesmoMotorista: false, mesmaRota: false, mesmaCarga: false, mesmoPeriodo: false, mesmoMetodo: false, comparador: '3', obs: '' },
 abast: [], trechos: [],
 tele: { rpmFaixa: '', marchaLenta: '', freioMotor: '', frenagens100: '', trocas100: '', cargaMotor: '', tempoMov: '', velMedia: '', cambioAuto: '', arlaPct: '', obs: '' },
 drv: { scores: {}, citacao: '', autorCitacao: '', escolha: '', comentarios: '' },
 tco: { precoMB: '', pag: 'fin', entrada: 0, prazo: 60, taxa: 1.35, taxaUnit: 'am', carencia: 3, carTipo: 'cap', horiz: 60, infDiesel: 5, arlaMB: 6, manutMB: '', dispMB: 96, deprecMB: 9, residualMB: '', ipva: 1.5, segPct: 3.2, pneusMB: '', taxaAplic: 10.5, receita: '', margem: 35, desagio: 5, custoVenda: 3, entradaC: 0, prazoC: 60, taxaC: '', carenciaC: 3, ipvaC: 1.5, segPctC: 3.3, dispC: '' },
 prop: { lote: '', modelo: '', preco: '', condicao: '', inclui: '', validade: '', decisao: '', criterio: '', passos: '', janela: '' },
 fotos: []
});
/* ---------- utilitários ---------- */
const num = v => { const n = parseFloat(String(v ?? '').replace(/\./g, '').replace(',', '.')); return isFinite(n) ? n : NaN; };
const numd = v => { const n = parseFloat(String(v ?? '').replace(',', '.')); return isFinite(n) ? n : NaN; };
const has = v => !(v === '' || v == null || (typeof v === 'number' && isNaN(v)));
const N = (v, d = 0) => has(v) && isFinite(+numd(v)) ? +numd(v) : d;
const dias = (a, b) => (a && b) ? Math.round((new Date(b) - new Date(a)) / 864e5) + 1 : 0;
/* ---------- motor de TCO (portado do tco-simulador) ---------- */
function finParams(v) {
 const iM = (v.taxaUnit || 'am') === 'am' ? N(v.taxa) / 100 : Math.pow(1 + N(v.taxa) / 100, 1 / 12) - 1;
 const car = Math.max(0, Math.min(36, Math.round(N(v.carencia)))), carTipo = v.carTipo || 'cap', fin = v.pag !== 'vista';
 const entrada = fin ? N(v.preco) * (N(v.entrada) / 100) : N(v.preco), pv = fin ? N(v.preco) - entrada : 0, prazo = Math.max(1, N(v.prazo, 60));
 const saldoPosCar = carTipo === 'cap' ? pv * Math.pow(1 + iM, car) : pv;
 const pmt = pv <= 0 ? 0 : (iM === 0 ? saldoPosCar / prazo : saldoPosCar * iM / (1 - Math.pow(1 + iM, -prazo)));
 return { iM, car, carTipo, fin, entrada, pv, prazo, pmt };
}
function simulate(v, g) {
 const H = Math.min(120, Math.max(1, N(g.horiz, 60))), disp = Math.max(0, Math.min(1, N(v.disp, 95) / 100));
 const infM = Math.pow(1 + N(g.infDiesel) / 100, 1 / 12) - 1, depM = 1 - Math.pow(1 - N(v.deprec) / 100, 1 / 12);
 const { iM, car, carTipo, fin, entrada, pv, prazo, pmt } = finParams(v);
 const kmEf = N(g.km) * disp, recDia = N(g.receita) / Math.max(1, N(g.diasOper, 25));
 let saldo = pv, vm = N(v.preco), baseAno = N(v.preco);
 let juros = 0, dieselC = 0, arlaC = 0, manutC = 0, pneusC = 0, ipvaC = 0, segC = 0, indispC = 0;
 const cum = [entrada]; let acc = entrada;
 for (let m = 1; m <= H; m++) {
  if (m > 1 && (m - 1) % 12 === 0) baseAno = vm;
  const pD = N(g.diesel) * Math.pow(1 + infM, m - 1), litros = N(v.kml) > 0 ? kmEf / N(v.kml) : 0;
  const cd = litros * pD, ca = litros * (N(v.arla) / 100) * N(g.arlaPreco) * Math.pow(1 + infM, m - 1);
  const cm = kmEf * N(v.manut), cpn = kmEf * N(v.pneus);
  const ci = baseAno * (N(v.ipva) / 100) / 12, cs = baseAno * (N(v.segPct) / 100) / 12;
  const cp = N(g.diasOper, 25) * (1 - disp) * recDia * (N(g.margem) / 100);
  dieselC += cd; arlaC += ca; manutC += cm; pneusC += cpn; ipvaC += ci; segC += cs; indispC += cp;
  let jMes = 0, pagoJ = 0, pagoA = 0;
  if (fin) {
   if (m <= car) { jMes = saldo * iM; if (carTipo === 'jur') pagoJ = jMes; else saldo += jMes; }
   else if (m <= car + prazo) { jMes = saldo * iM; const amort = pmt - jMes; saldo = Math.max(0, saldo - amort); pagoJ = jMes; pagoA = amort; }
  }
  juros += jMes; vm *= (1 - depM);
  acc += cd + ca + cm + cpn + ci + cs + cp + pagoJ + pagoA; cum.push(acc);
 }
 const residualBase = N(v.residualPct) > 0 ? N(v.preco) * N(v.residualPct) / 100 : vm;
 const residual = residualBase * (1 - (N(g.desagio) + N(g.custoVenda)) / 100);
 const opex = dieselC + arlaC + manutC + pneusC + ipvaC + segC + indispC, tco = N(v.preco) + juros + opex - residual, kmTot = kmEf * H;
 return { H, entrada, pmt, juros, dieselC, arlaC, manutC, pneusC, ipvaC, segC, indispC, opex, vm, residual, tco, kmTot, tcoKm: kmTot > 0 ? tco / kmTot : 0, tcoMes: tco / H, cum };
}
function compare(M, C, g) {
 const rm = simulate(M, g), rc = simulate(C, g);
 let payback = null;
 for (let i = 1; i < rm.cum.length; i++) if (rm.cum[i] <= rc.cum[i]) { payback = i; break; }
 return { M, C, rm, rc, delta: rm.tco - rc.tco, deltaPct: rc.tco ? (rm.tco - rc.tco) / Math.abs(rc.tco) : 0, payback };
}
/* ---------- cálculos do teste ---------- */
function calc(T) {
 const R = { gaps: [] };
 const gap = (p, campo, motivo) => R.gaps.push({ p, campo, motivo });
 // protocolo
 R.dias = dias(T.prot.inicio, T.prot.fim);
 const ab = [...T.abast].filter(a => has(a.odometro) && has(a.litros)).sort((a, b) => N(a.odometro) - N(b.odometro));
 R.nAbast = ab.length;
 if (ab.length >= 2) { R.kmBomba = N(ab[ab.length - 1].odometro) - N(ab[0].odometro); R.litrosBomba = ab.slice(1).reduce((s, a) => s + N(a.litros), 0); R.kmlBomba = R.litrosBomba > 0 ? R.kmBomba / R.litrosBomba : NaN; }
 // trechos
 const tr = T.trechos.filter(t => N(t.km) > 0);
 R.nTrechos = tr.length; R.kmTrechos = tr.reduce((s, t) => s + N(t.km), 0);
 const litros = t => N(t.litros) > 0 ? N(t.litros) : (N(t.kmlFb) > 0 ? N(t.km) / N(t.kmlFb) : 0);
 const grp = cond => { const g = tr.filter(t => t.cond === cond && litros(t) > 0); const km = g.reduce((s, t) => s + N(t.km), 0), l = g.reduce((s, t) => s + litros(t), 0); return { n: g.length, km, l, kml: l > 0 ? km / l : NaN, min: g.length ? Math.min(...g.map(t => N(t.km) / litros(t))) : NaN, max: g.length ? Math.max(...g.map(t => N(t.km) / litros(t))) : NaN }; };
 R.car = grp('carregado'); R.vaz = grp('vazio'); R.par = grp('parcial');
 const allL = tr.filter(t => litros(t) > 0), kmA = allL.reduce((s, t) => s + N(t.km), 0), lA = allL.reduce((s, t) => s + litros(t), 0);
 R.kmlFb = lA > 0 ? kmA / lA : NaN;
 R.pctCarregado = R.kmTrechos > 0 ? 100 * (R.car.km + R.par.km) / R.kmTrechos : NaN;
 const mix = N(T.op.mixCarregado, 50) / 100;
 R.kmlPond = (R.car.kml > 0 && R.vaz.kml > 0) ? 1 / (mix / R.car.kml + (1 - mix) / R.vaz.kml) : (R.car.kml > 0 ? R.car.kml : R.kmlFb);
 R.kmlMB = R.kmlPond > 0 ? R.kmlPond : (R.kmlBomba > 0 ? R.kmlBomba : NaN);
 R.fonteKml = R.kmlPond > 0 ? 'trechos (Fleetboard, ponderado pelo mix)' : (R.kmlBomba > 0 ? 'bomba (tanque cheio a tanque cheio)' : '');
 R.difMetodos = (R.kmlBomba > 0 && R.kmlFb > 0) ? (R.kmlFb - R.kmlBomba) / R.kmlBomba : NaN;
 // RDI
 const rdi = (alt, par, urb, vel) => { const a = N(alt), p = N(par), u = N(urb), v = N(vel); if (!(a || p)) return NaN; /* sem altitude nem paradas o índice não caracteriza a rota */ return +(0.35 * (a / 500) + 0.25 * (p / 5) + 0.25 * (u / 100) + 0.15 * (v > 0 ? 50 / v : 1)).toFixed(3); };
 const kmT = R.kmTrechos || 1;
 const altT = tr.reduce((s, t) => s + N(t.ganhoAlt), 0) / kmT * 100, parT = tr.reduce((s, t) => s + N(t.paradas), 0) / kmT * 100;
 const urbT = tr.reduce((s, t) => s + N(t.urbano) * N(t.km), 0) / kmT, velT = tr.filter(t => N(t.velMedia) > 0);
 const velTm = velT.length ? velT.reduce((s, t) => s + N(t.velMedia) * N(t.km), 0) / velT.reduce((s, t) => s + N(t.km), 0) : N(T.tele.velMedia);
 R.rdiTeste = tr.length ? rdi(altT, parT, urbT, velTm) : NaN;
 R.rdiOp = rdi(T.op.ganhoAlt, T.op.paradas100, 100 - N(T.op.perfilRod, 100), T.op.velMedia);
 R.aderencia = (R.rdiTeste > 0 && R.rdiOp > 0) ? Math.max(0, 1 - Math.abs(R.rdiTeste - R.rdiOp) / R.rdiOp) : NaN;
 R.altT = altT; R.parT = parT; R.urbT = urbT; R.velT = velTm;
 // baseline / benchmark
 const kml0 = N(T.base.kml), diesel = N(T.base.diesel), kmMes = N(T.op.kmMes);
 R.kml0 = kml0; R.l100MB = R.kmlMB > 0 ? 100 / R.kmlMB : NaN; R.l1000 = kml0 > 0 && R.kmlMB > 0 ? 100 / kml0 : NaN;
 R.l100Atual = kml0 > 0 ? 100 / kml0 : NaN; R.l100Menos = (R.l100Atual > 0 && R.l100MB > 0) ? R.l100Atual - R.l100MB : NaN;
 R.l100MenosCar = (R.l100Atual > 0 && R.car.kml > 0) ? R.l100Atual - 100 / R.car.kml : NaN;
 R.ganhoKmlPct = (kml0 > 0 && R.kmlMB > 0) ? (R.kmlMB - kml0) / kml0 : NaN;
 R.econDieselMes = (kmMes > 0 && diesel > 0 && R.l100Menos === R.l100Menos) ? kmMes * R.l100Menos / 100 * diesel : NaN;
 R.valor01kml = (kmMes > 0 && diesel > 0 && kml0 > 0) ? (kmMes / kml0 - kmMes / (kml0 + 0.1)) * diesel * 12 : NaN;
 R.valorDiaParado = N(T.base.custoDiaParado) > 0 ? N(T.base.custoDiaParado) : (N(T.tco.receita) > 0 ? N(T.tco.receita) / N(T.op.diasOper, 25) * N(T.tco.margem, 35) / 100 : NaN);
 // opex atual por km
 const arlaP = N(T.base.arlaPreco, 3.5);
 const opexKm = (kml, arla, manut, pneus, dParados) => { if (!(kml > 0 && diesel > 0)) return null; const comb = diesel / kml, ar = (arla / 100) * arlaP / kml, ma = N(manut), pn = N(pneus); const pa = (dParados > 0 && R.valorDiaParado > 0 && kmMes > 0) ? dParados * R.valorDiaParado / (kmMes * 12) : 0; return { comb, ar, ma, pn, pa, total: comb + ar + ma + pn + pa }; };
 R.opexAtual = opexKm(kml0, N(T.base.arla, 6), T.base.manut, T.base.pneus, N(T.base.diasParados));
 R.opexMB = opexKm(R.kmlMB, N(T.tco.arlaMB, 6), T.tco.manutMB, T.tco.pneusMB, N(T.op.diasOper, 25) * 12 * (1 - N(T.tco.dispMB, 96) / 100));
 R.opexDelta = (R.opexAtual && R.opexMB) ? R.opexAtual.total - R.opexMB.total : NaN;
 R.opexShareComb = R.opexAtual ? R.opexAtual.comb / R.opexAtual.total : NaN;
 // equivalência do benchmark
 const chk = ['mesmoMotorista', 'mesmaRota', 'mesmaCarga', 'mesmoPeriodo', 'mesmoMetodo'];
 R.equivOk = chk.filter(k => T.prot[k]).length; R.equivFalhas = chk.length - R.equivOk;
 R.equivalente = R.equivFalhas < 2;
 // TCO (3 cenários)
 const g = { km: kmMes, horiz: N(T.tco.horiz, 60), diasOper: N(T.op.diasOper, 25), diesel, infDiesel: N(T.tco.infDiesel, 5), arlaPreco: arlaP, receita: N(T.tco.receita), margem: N(T.tco.margem, 35), desagio: N(T.tco.desagio, 5), custoVenda: N(T.tco.custoVenda, 3) };
 const M0 = { preco: N(T.tco.precoMB), pag: T.tco.pag, entrada: N(T.tco.entrada), prazo: N(T.tco.prazo, 60), taxa: N(T.tco.taxa), taxaUnit: T.tco.taxaUnit || 'am', carencia: N(T.tco.carencia), carTipo: T.tco.carTipo || 'cap', kml: R.kmlMB, arla: N(T.tco.arlaMB, 6), manut: N(T.tco.manutMB), pneus: N(T.tco.pneusMB), disp: N(T.tco.dispMB, 96), deprec: N(T.tco.deprecMB, 9), residualPct: N(T.tco.residualMB), ipva: N(T.tco.ipva, 1.5), segPct: N(T.tco.segPct, 3.2) };
 const C0 = { preco: N(T.base.precoNovo), pag: T.tco.pag, entrada: N(T.tco.entradaC), prazo: N(T.tco.prazoC, 60), taxa: N(T.tco.taxaC, N(T.tco.taxa)), taxaUnit: T.tco.taxaUnit || 'am', carencia: N(T.tco.carenciaC), carTipo: T.tco.carTipo || 'cap', kml: kml0, arla: N(T.base.arla, 6), manut: N(T.base.manut), pneus: N(T.base.pneus), disp: N(T.tco.dispC, N(T.base.disp, 95)), deprec: N(T.base.deprec, 10), residualPct: N(T.base.residualPct), ipva: N(T.tco.ipvaC, 1.5), segPct: N(T.tco.segPctC, 3.3) };
 R.tcoOk = M0.preco > 0 && C0.preco > 0 && M0.kml > 0 && C0.kml > 0 && diesel > 0 && kmMes > 0;
 if (R.tcoOk) {
  const kmlCons = R.car.min > 0 && R.car.kml > 0 ? R.kmlMB * Math.min(1, R.car.min / R.car.kml) : R.kmlMB * 0.95;
  const kmlOtim = R.car.max > 0 && R.car.kml > 0 ? R.kmlMB * Math.max(1, R.car.max / R.car.kml) : R.kmlMB * 1.05;
  R.cen = {
   conservador: compare({ ...M0, kml: kmlCons, residualPct: M0.residualPct > 0 ? M0.residualPct - 5 : 0, deprec: M0.deprec + 1, disp: Math.min(M0.disp, C0.disp || M0.disp) }, { ...C0, kml: kml0 * 1.03 }, { ...g, diesel: diesel * 1.1 }),
   realista: compare(M0, C0, g),
   otimista: compare({ ...M0, kml: kmlOtim }, C0, g)
  };
  R.cenKml = { conservador: kmlCons, realista: R.kmlMB, otimista: kmlOtim };
  R.tco = R.cen.realista;
  const econAno = c => (c.rc.tco - c.rm.tco) / c.rm.H * 12;
  R.econAno = { conservador: econAno(R.cen.conservador), realista: econAno(R.cen.realista), otimista: econAno(R.cen.otimista) };
  R.econKm = { conservador: R.cen.conservador.rc.tcoKm - R.cen.conservador.rm.tcoKm, realista: R.tco.rc.tcoKm - R.tco.rm.tcoKm, otimista: R.cen.otimista.rc.tcoKm - R.cen.otimista.rm.tcoKm };
  // sensibilidade (realista)
  const base = R.tco.rc.tco - R.tco.rm.tco;
  const sens = (lbl, fM, fC, fg) => { const r = compare(fM ? fM(M0) : M0, fC ? fC(C0) : C0, fg ? fg(g) : g); return { lbl, v: (r.rc.tco - r.rm.tco) - base }; };
  R.sens = [
   sens('Consumo MB −10%', m => ({ ...m, kml: m.kml * 0.9 })), sens('Consumo MB +10%', m => ({ ...m, kml: m.kml * 1.1 })),
   sens('Consumo atual +5%', null, c => ({ ...c, kml: c.kml * 1.05 })),
   sens('Diesel −10%', null, null, x => ({ ...x, diesel: x.diesel * 0.9 })), sens('Diesel +20%', null, null, x => ({ ...x, diesel: x.diesel * 1.2 })),
   sens('km/mês 70%', null, null, x => ({ ...x, km: x.km * 0.7 })), sens('km/mês 130%', null, null, x => ({ ...x, km: x.km * 1.3 })),
   sens('Taxa MB +0,3 p.p.', m => ({ ...m, taxa: m.taxa + (m.taxaUnit === 'am' ? 0.3 : 3.6) })),
   sens('Residual MB −10 p.p.', m => ({ ...m, residualPct: m.residualPct > 0 ? m.residualPct - 10 : 0, deprec: m.deprec + 2 })),
   sens('Manutenção MB +30%', m => ({ ...m, manut: m.manut * 1.3 }))
  ];
  R.baseDelta = base;
  const n = [1, 5, 10, N(T.cli.frotaElegivel) || 0].filter((x, i, a) => x > 0 && a.indexOf(x) === i).sort((a, b) => a - b);
  R.escala = n.map(k => ({ n: k, ano: R.econAno.conservador * k, cinco: R.econAno.conservador * k * 5, anoR: R.econAno.realista * k }));
 } else {
  if (!(M0.preco > 0)) gap('P0', 'Preço do Mercedes-Benz (TCO)', 'sem preço não há TCO');
  if (!(C0.preco > 0)) gap('P0', 'Preço do veículo de referência novo (baseline)', 'sem preço não há TCO comparativo');
  if (!(kml0 > 0)) gap('P0', 'Consumo real da frota atual (km/L)', 'sem baseline não há benchmark nem TCO');
  if (!(diesel > 0)) gap('P1', 'Preço do diesel pago pelo cliente', 'TCO usa preço de mercado declarado');
  if (!(kmMes > 0)) gap('P0', 'Quilometragem mensal do cliente', 'sem km/mês não há impacto financeiro');
 }
 // driver
 const sc = T.drv.scores || {}; let wa = 0, wm = 0, ws = 0, na = 0;
 R.drvRows = DRV_CRIT.map(([k, l, w]) => { const a = N(sc[k]?.atual), m = N(sc[k]?.mb); if (a > 0 && m > 0) { wa += a * w; wm += m * w; ws += w; na++; } return { k, l, w, atual: a, mb: m }; });
 R.drvAtual = ws ? wa / ws : NaN; R.drvMB = ws ? wm / ws : NaN; R.drvN = na;
 R.drvMaior = R.drvRows.filter(r => r.atual > 0 && r.mb > 0).sort((a, b) => (b.mb - b.atual) - (a.mb - a.atual)).slice(0, 2);
 // compatibilidade
 R.compat = COMPAT_ITEMS.map(([k, l]) => { const a = String(T.vt[k] || '').trim(), b = String(T.vo[k] || '').trim(); const st = T.compat[k]?.status || (a && b ? (a.toLowerCase() === b.toLowerCase() ? 'identico' : 'diferente') : 'pendente'); return { k, l, a, b, st, nota: T.compat[k]?.nota || '' }; });
 R.compatId = R.compat.filter(c => c.st === 'identico').length; R.compatEq = R.compat.filter(c => c.st === 'equivalente').length;
 R.compatDif = R.compat.filter(c => c.st === 'diferente'); R.compatPend = R.compat.filter(c => c.st === 'pendente').length;
 // gaps P0 gerais
 if (!T.cli.empresa) gap('P0', 'Empresa', 'identificação');
 if (!R.dias) gap('P0', 'Período do teste', 'protocolo');
 if (!(R.kmlMB > 0)) gap('P0', 'Consumo medido (trechos ou abastecimentos)', 'sem consumo não há prova');
 if (!tr.length) gap('P0', 'Trechos com carga e consumo', 'objeção "estava vazio" sem resposta; rota sem RDI');
 if (tr.length && !tr.some(t => N(t.cargaT) > 0)) gap('P0', 'Carga por trecho (t)', 'sem peso não há normalização');
 if (!(R.rdiOp > 0)) gap('P1', 'Perfil da operação normal (altitude, paradas, % rodoviário, velocidade)', 'aderência do teste não pode ser medida');
 if (R.compatPend) gap('P0', 'Ficha testado × ofertado (' + R.compatPend + ' itens em branco)', 'resultado pode ser usado para configuração diferente');
 if (!has(T.tele.rpmFaixa)) gap('P1', 'Telemetria: tempo em faixa econômica', 'sem explicação causal do consumo');
 if (!R.drvN) gap('P1', 'Driver Scorecard', 'percepção fica em texto livre');
 if (!(N(T.base.manut) > 0)) gap('P1', 'Manutenção da frota atual (R$/km)', 'TCO atual usa referência');
 if (!T.fotos.length) gap('P2', 'Fotografias do veículo na operação', 'capa e evidências visuais');
 if (!T.cli.logo) gap('P2', 'Logomarca do cliente', 'capa');
 R.completude = Math.max(0, Math.round(100 * (1 - (R.gaps.filter(x => x.p === 'P0').length * 0.12 + R.gaps.filter(x => x.p === 'P1').length * 0.05 + R.gaps.filter(x => x.p === 'P2').length * 0.02))));
 return R;
}
return { NEW, uid, DRV_CRIT, COMPAT_ITEMS, num, numd, has, N, dias, finParams, simulate, compare, calc };
})();
