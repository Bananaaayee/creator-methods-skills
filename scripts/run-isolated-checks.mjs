#!/usr/bin/env node
// Replay installer discovery/copy checks with official CLIs already installed in
// a separate tooling directory. No package downloads, models, or login occur here.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const options = {};
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--help') { options.help = true; continue; }
  if (!['--tooling','--repo','--archives','--phase'].includes(argv[i]) || !argv[i + 1]) throw new Error(`Unknown or missing option: ${argv[i]}`);
  options[argv[i].slice(2)] = argv[++i];
}
if (options.help) {
  console.log('Usage: node scripts/run-isolated-checks.mjs --tooling <directory> [--repo <directory>] [--archives <directory>] [--phase final-local|candidate|final-archive|all-local|versions|remote|remote-multi]');
  console.log('Default phase: final-local. Local state/results are created in a fresh system temporary directory. Remote phases explicitly access only the public Vercel control repository.');
  process.exit(0);
}
if (!options.tooling) throw new Error('--tooling is required; see tests/installation/README.md');
const requestedPhase = options.phase || 'final-local';
const source = path.resolve(options.repo || path.join(scriptDir, '..'));
const archiveDir = path.resolve(options.archives || path.join(source, '..', 'release-assets'));
const tooling = path.resolve(options.tooling);
const node = process.execPath;
const npx = path.join(tooling, 'node_modules/npm/bin/npx-cli.js');
const gemini = path.join(tooling, 'node_modules/@google/gemini-cli/bundle/gemini.js');
for (const file of [npx, gemini, path.join(tooling,'node_modules/skills/bin/cli.mjs')]) await fs.access(file);
const base = await fs.mkdtemp(path.join(os.tmpdir(), 'creator-atlas-install-checks-'));
const recordDir = path.join(base, 'results');
await fs.mkdir(recordDir);
const nullFile = process.platform === 'win32' ? 'NUL' : '/dev/null';
const systemPaths = process.platform === 'win32' ? [path.join(process.env.SystemRoot || 'C:/Windows','System32')] : ['/usr/bin','/bin','/usr/sbin','/sbin'];
const env = {
  PATH: [path.dirname(node),path.join(tooling,'node_modules/.bin'),...systemPaths].join(path.delimiter),
  LANG: 'en_US.UTF-8', TERM: 'dumb', CI: '1',
  XDG_STATE_HOME: path.join(base,'xdg-state'), XDG_CONFIG_HOME: path.join(base,'xdg-config'),
  XDG_CACHE_HOME: path.join(base,'xdg-cache'), XDG_DATA_HOME: path.join(base,'xdg-data'),
  npm_config_cache: path.join(base,'npm-cache'), npm_config_userconfig: nullFile,
  npm_config_update_notifier: 'false',
  GEMINI_CLI_HOME: path.join(base,'gemini-home'), GEMINI_CLI_NO_RELAUNCH: '1',
  GEMINI_CLI_TRUST_WORKSPACE: 'true', GEMINI_TELEMETRY_ENABLED: 'false',
  DISABLE_TELEMETRY: '1', DO_NOT_TRACK: '1', NODE_DISABLE_COMPILE_CACHE: '1',
  GIT_CONFIG_GLOBAL: nullFile, GIT_CONFIG_SYSTEM: nullFile, GIT_TERMINAL_PROMPT: '0',
  GIT_SSH_COMMAND: `ssh -o BatchMode=yes -o IdentitiesOnly=yes -o IdentityFile=${nullFile} -o StrictHostKeyChecking=yes`
};
if (process.platform === 'win32' && process.env.SystemRoot) env.SystemRoot = process.env.SystemRoot;
for (const p of [env.XDG_STATE_HOME,env.XDG_CONFIG_HOME,env.XDG_CACHE_HOME,env.XDG_DATA_HOME,env.GEMINI_CLI_HOME]) await fs.mkdir(p,{recursive:true});
await fs.mkdir(path.join(env.GEMINI_CLI_HOME,'.gemini'),{recursive:true});
const temporarySettings = JSON.stringify({advanced:{autoConfigureMemory:false},telemetry:{enabled:false}});
await fs.writeFile(path.join(env.GEMINI_CLI_HOME,'settings.json'),temporarySettings);
await fs.writeFile(path.join(env.GEMINI_CLI_HOME,'.gemini/settings.json'),temporarySettings);
const skillsArgs = (...args) => [npx,'--prefix',tooling,'--no','--','skills',...args];
let phase;
let results;

async function run(id, args, cwd, expectNames = [], expectCode = 0) {
  await fs.mkdir(cwd, { recursive: true });
  const start = new Date().toISOString();
  const result = await new Promise((resolve) => {
    const child = spawn(node, args, {cwd, env, detached:process.platform !== 'win32', stdio:['ignore','pipe','pipe']});
    let stdout = '', stderr = '', timedOut = false;
    child.stdout.on('data', d => stdout += d);
    child.stderr.on('data', d => stderr += d);
    const timeout = setTimeout(() => {
      timedOut = true;
      try {
        if (process.platform !== 'win32') process.kill(-child.pid, 'SIGKILL');
        else child.kill('SIGKILL');
      } catch { /* The process group may already have exited. */ }
    }, 55000);
    child.on('error', error => { clearTimeout(timeout); resolve({exitCode:null,stdout,stderr,error:String(error),timedOut}); });
    child.on('close', code => { clearTimeout(timeout); resolve({exitCode:code,stdout,stderr,timedOut}); });
  });
  const clean = s => s.replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, '');
  result.stdout = clean(result.stdout); result.stderr = clean(result.stderr);
  const output = result.stdout + result.stderr;
  const passed = result.exitCode === expectCode && !result.timedOut && expectNames.every(n => output.includes(n));
  const entry = {id, start, cwd, executable:node, args, expectNames, expectCode, passed, ...result};
  results.push(entry);
  await fs.writeFile(path.join(recordDir, `${phase}-${id}.log`), `COMMAND: ${node} ${args.join(' ')}\nCWD: ${cwd}\nEXIT: ${result.exitCode}\n\n${output}`);
  console.log(JSON.stringify({id, exitCode:result.exitCode, passed, outputTail:output.slice(-500)}));
  return entry;
}

async function fileHashes(dir, prefix = '') {
  const entries = await fs.readdir(dir, {withFileTypes:true});
  const hashes = {};
  for (const e of entries.sort((a,b) => a.name.localeCompare(b.name))) {
    const p = path.join(dir,e.name), rel = prefix ? `${prefix}/${e.name}` : e.name;
    if (e.isDirectory()) Object.assign(hashes, await fileHashes(p,rel));
    else if (e.isFile()) hashes[rel] = createHash('sha256').update(await fs.readFile(p)).digest('hex');
    else if (e.isSymbolicLink()) hashes[rel] = `symlink:${await fs.readlink(p)}`;
  }
  return hashes;
}

async function compareInstalled(id, repo, target, selectedNames = names) {
  const checks = [];
  for (const name of selectedNames) {
    const original = await fileHashes(`${repo}/skills/${name}`);
    let installed = null, error = null;
    try { installed = await fileHashes(`${target}/${name}`); } catch(e) {error = String(e);}
    checks.push({name, files:Object.keys(original).length, identical:JSON.stringify(original) === JSON.stringify(installed), original, installed, error});
  }
  const result = {id, target, passed:checks.every(c=>c.identical), checks};
  results.push(result);
  console.log(JSON.stringify({id,target,passed:result.passed,checks:checks.map(c=>({name:c.name,files:c.files,identical:c.identical,error:c.error}))}));
}

const names = ['he-tongxue-creator','lawrence-creator','media-storm-creator'];
const phases = requestedPhase === 'all-local' ? ['candidate','final-local','final-archive'] : [requestedPhase];
for (const selectedPhase of phases) {
phase = selectedPhase;
results = [];
if (phase === 'candidate') {
  if (!source) throw new Error('candidate source directory required');
  const repo = path.resolve(source);
  await run('vercel-list-root', skillsArgs('add', repo, '--list'), `${base}/candidate-vercel-list-root`, names);
  for (const name of names) await run(`vercel-list-${name}`, skillsArgs('add', `${repo}/skills/${name}`, '--list'), `${base}/candidate-vercel-list-${name}`, [name]);
  await run('vercel-install-all', skillsArgs('add', repo, '--skill', '*', '-a', 'codex', 'gemini-cli', '--copy', '-y'), `${base}/candidate-vercel-install-all`, names);
  await run('vercel-installed-list', skillsArgs('list', '--json'), `${base}/candidate-vercel-install-all`, names);
  await compareInstalled('vercel-installed-file-hashes', repo, `${base}/candidate-vercel-install-all/.agents/skills`);
  await run('gemini-discovers-vercel-agents-alias', [gemini,'skills','list'], `${base}/candidate-vercel-install-all`, names);
  for (const name of names) {
    const target = `${base}/candidate-vercel-install-${name}`;
    await run(`vercel-install-${name}`, skillsArgs('add', repo, '--skill', name, '-a', 'codex', 'gemini-cli', '--copy', '-y'), target, [name]);
    await compareInstalled(`vercel-install-${name}-file-hashes`, repo, `${target}/.agents/skills`, [name]);
  }
  await run('gemini-root-negative', [gemini,'skills','install',repo,'--scope','workspace','--consent'], `${base}/candidate-gemini-root-negative`, ['No valid skills found'], 1);
  await run('gemini-install-container', [gemini,'skills','install',`${repo}/skills`,'--scope','workspace','--consent'], `${base}/candidate-gemini-install-container`, names);
  await run('gemini-installed-list', [gemini,'skills','list'], `${base}/candidate-gemini-install-container`, names);
  await compareInstalled('gemini-installed-file-hashes', repo, `${base}/candidate-gemini-install-container/.gemini/skills`);
  for (const name of names) {
    const target = `${base}/candidate-gemini-install-${name}`;
    await run(`gemini-install-${name}`, [gemini,'skills','install',`${repo}/skills/${name}`,'--scope','workspace','--consent'], target, [name]);
    await compareInstalled(`gemini-install-${name}-file-hashes`, repo, `${target}/.gemini/skills`, [name]);
  }
} else if (phase === 'remote') {
  await run('vercel-list-github-root', skillsArgs('add','https://github.com/vercel-labs/agent-skills','--list'), `${base}/remote-vercel-list-root`, ['web-design-guidelines']);
  await run('vercel-list-github-subdir', skillsArgs('add','https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines','--list'), `${base}/remote-vercel-list-subdir`, ['web-design-guidelines']);
  await run('gemini-install-github-subdir', [gemini,'skills','install','https://github.com/vercel-labs/agent-skills.git','--path','skills/web-design-guidelines','--scope','workspace','--consent'], `${base}/remote-gemini-install-subdir`, ['web-design-guidelines']);
} else if (phase === 'remote-multi') {
  await run('gemini-root-negative', [gemini,'skills','install','https://github.com/vercel-labs/agent-skills.git','--scope','workspace','--consent'], `${base}/remote-gemini-root-negative`, ['No valid skills found'], 1);
  await run('gemini-install-container', [gemini,'skills','install','https://github.com/vercel-labs/agent-skills.git','--path','skills','--scope','workspace','--consent'], `${base}/remote-gemini-install-container`, ['web-design-guidelines','writing-guidelines','vercel-react-best-practices']);
  await run('gemini-installed-list', [gemini,'skills','list'], `${base}/remote-gemini-install-container`, ['web-design-guidelines','writing-guidelines','vercel-react-best-practices']);

} else if (phase === 'final-local') {
  if (!source) throw new Error('final source directory required');
  const repo = path.resolve(source);
  await run('vercel-list-root', skillsArgs('add', repo, '--list'), `${base}/final-vercel-list-root`, [...names,'Found 3 skills']);
  await run('vercel-install-claude-code', skillsArgs('add', repo, '--skill', '*', '-a', 'claude-code', '--copy', '-y'), `${base}/final-vercel-install-claude-code`, names);
  await run('vercel-list-claude-code', skillsArgs('list', '--json', '-a', 'claude-code'), `${base}/final-vercel-install-claude-code`, names);
  await compareInstalled('vercel-claude-code-file-hashes', repo, `${base}/final-vercel-install-claude-code/.claude/skills`);
  await run('gemini-install-container', [gemini,'skills','install',`${repo}/skills`,'--scope','workspace','--consent'], `${base}/final-gemini-install-container`, names);
  await run('gemini-installed-list', [gemini,'skills','list'], `${base}/final-gemini-install-container`, names);
  await compareInstalled('gemini-installed-file-hashes', repo, `${base}/final-gemini-install-container/.gemini/skills`);
} else if (phase === 'final-archive') {
  if (!source) throw new Error('final source directory required');
  const repo = path.resolve(source);
  const name = names[0];
  const original = path.join(archiveDir, `${name}.zip`);
  const temporarySkillArchive = `${base}/${name}.skill`;
  await fs.copyFile(original, temporarySkillArchive);
  await run('gemini-ordinary-zip-negative', [gemini,'skills','install',original,'--scope','workspace','--consent'], `${base}/final-gemini-ordinary-zip-negative`, ['No valid skills found'], 1);
  await run('gemini-skill-archive-install', [gemini,'skills','install',temporarySkillArchive,'--scope','workspace','--consent'], `${base}/final-gemini-skill-archive-install`, [name]);
  await run('gemini-skill-archive-list', [gemini,'skills','list'], `${base}/final-gemini-skill-archive-install`, [name]);
  await compareInstalled('gemini-skill-archive-file-hashes', repo, `${base}/final-gemini-skill-archive-install/.gemini/skills`, [name]);
  results.push({id:'archive-byte-copy', original, temporarySkillArchive, passed:Buffer.compare(await fs.readFile(original),await fs.readFile(temporarySkillArchive)) === 0});
} else if (phase === 'versions') {
  await run('skills-version', skillsArgs('--version'), `${base}/versions`, ['1.7.4']);
  await run('gemini-version', [gemini,'--version'], `${base}/versions`, ['0.65.0']);
  await run('gemini-install-help', [gemini,'skills','install','--help'], `${base}/versions`, ['--path','--scope','--consent']);
} else throw new Error(`Unknown phase: ${phase}`);

await fs.writeFile(path.join(recordDir, `${phase}-results.json`), JSON.stringify({phase, source, checkedAt:new Date().toISOString(), isolation:{base, inheritedEnvironment:false, modelCalls:false, credentialInputs:false, homeOverridden:false, codexHomeOverridden:false, temporaryWorkspaceTrust:'GEMINI_CLI_TRUST_WORKSPACE=true only for isolated child process', redirectedState:['XDG_STATE_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','GEMINI_CLI_HOME']}, results}, null, 2));
if (results.some(r => !r.passed)) process.exitCode = 1;
}
console.log(`Results and temporary project files: ${base}`);
