// node tools/independent_checks/energy_grid.mjs index.html in.json out.json
// Helper for check_energy_drains.py (build queue 060, roadmap/ewar-plan.md phase B): loads index.html's script in a Node vm
// (no page, no network), then for each case evaluates PYFA CORE projected pyfaEnergyDrainsAt (the drains an attacker's
// neutralizers, nosferatu, EV drones and Cenobites put on a target at a distance) and, when the case carries the target's
// capacitor simulation inputs, PYFA CORE cap-sim capSimPyfa on its best case plus those drains.
// in.json: {srcs: {fitId: estimate.application.projected}, cases: [{src, tgt: {resist, disallow, sig}, d, sim?: {capacity, rechargeMs, best}}]}
// out.json: [{drains, sim?}] in the order of the cases
import fs from 'fs'; import vm from 'vm';
const [htmlPath, inPath, outPath] = process.argv.slice(2);
const code = [...fs.readFileSync(htmlPath, 'utf8').matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
const fakeEl = () => ({addEventListener(){}, get style(){return {};}, querySelectorAll(){return [];}, appendChild(){}, innerHTML: ''});
const sb = {fetch: async () => ({ok: false, status: 404}), document: {getElementById: fakeEl, createElement: fakeEl}, console: {log(){}, warn(){}, error(){}},
  Promise, Map, Set, Infinity, Math, JSON, Object, Array, Number, String};
vm.createContext(sb); vm.runInContext(code, sb);
const {srcs, cases} = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const out = cases.map(c => {
  const drains = sb.pyfaEnergyDrainsAt(srcs[c.src], c.tgt, c.d);
  const r = {drains};
  if(c.sim){
    const s = sb.capSimPyfa(c.sim.capacity, c.sim.rechargeMs, [...c.sim.best, ...drains]);
    r.sim = {stable: s.stable, stablePct: s.stablePct, timeToEmptyExactSec: s.timeToEmptyExactSec === undefined ? null : s.timeToEmptyExactSec};
  }
  return r;
});
fs.writeFileSync(outPath, JSON.stringify(out));
