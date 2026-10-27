import { cp, mkdir, readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const web = path.join(root, 'web');
const out = path.join(root, 'dist');
const data = JSON.parse(await readFile(path.join(web, 'data/project.json'), 'utf8'));
if (!data.source?.csv_sha256 || !data.views?.raw?.['all|all']) throw new Error('Verified public data missing. Run scripts/export_publication.py locally.');
for (const name of ['index.html', 'evidence.html', 'styles.css', 'app.js', 'favicon.svg', 'data/references.json']) {
  await stat(path.join(web, name));
}
await mkdir(out, { recursive: true });
await cp(web, out, { recursive: true, filter: file => !file.endsWith('.template.html') });
console.log(`Built static research site: ${data.summary.raw_rows} source records. No build dependencies or network required.`);
