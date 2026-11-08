// The served copy's script without comments (build queue 027; Project doc roadmap/page-publish-plan.md).
//
//     node tools/publish/strip_js.js < script.js > stripped.js
//
// acorn (tools/publish/acorn.js, MIT, a copy of acorn 8.18.0's dist/acorn.js; acorn-LICENSE) reads the script as the browser
// does and lists its tokens. The output is every token's own text, copied as is, with what lay between two tokens (spaces and
// comments) replaced by one line break if it held one (so the script's automatic semicolons stay where they were), else by one
// space, else nothing. Strings, template literals and regular expressions are tokens, so nothing inside them can change.
// Then the output is read again and its tokens must be the source's, one for one: only comments and spaces went.
// Exits 1 with the reason on anything else (the publish step stops; nothing is published).
'use strict';
const acorn = require('./acorn.js');
const OPT = {ecmaVersion: 'latest', sourceType: 'script', allowHashBang: false};

// Each token as [its text, whether a line break comes before it]: a line break (one inside a comment counts too) decides
// where the script gets its automatic semicolons ("return" then a value on the next line returns nothing), so it must survive.
const NL = /[\n\r\u2028\u2029]/;
function tokens(src){
  acorn.parse(src, OPT);                                   // the whole script must parse, not only tokenize
  const spans = [...acorn.tokenizer(src, OPT)].map(t => [t.start, t.end]);
  const list = spans.map(([s, e], i) => [src.slice(s, e), i > 0 && NL.test(src.slice(spans[i - 1][1], s))]);
  return {list, spans};
}

function strip(src){
  const {spans} = tokens(src);
  let out = '', prev = 0;
  for(const [s, e] of spans){
    const gap = src.slice(prev, s);
    if(out){
      if(NL.test(gap)) out += '\n';
      else if(gap) out += ' ';
    }
    out += src.slice(s, e); prev = e;
  }
  return out + '\n';
}

function main(){
  const src = require('fs').readFileSync(0, 'utf8');
  let out;
  try{ out = strip(src); }catch(e){ process.stderr.write(`STRIP JS: the script doesn't parse: ${e.message}\n`); process.exit(1); }
  const a = tokens(src).list, b = tokens(out).list;
  if(a.length !== b.length){ process.stderr.write(`STRIP JS: ${a.length} tokens before, ${b.length} after\n`); process.exit(1); }
  for(let i = 0; i < a.length; i++) if(a[i][0] !== b[i][0] || a[i][1] !== b[i][1]){ process.stderr.write(`STRIP JS: token ${i} changed: ${JSON.stringify(a[i]).slice(0, 80)} -> ${JSON.stringify(b[i]).slice(0, 80)}\n`); process.exit(1); }
  process.stdout.write(out);
}

if(require.main === module) main();
module.exports = {strip, tokens};
