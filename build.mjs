import {mkdir,copyFile,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist/data',{recursive:true});
for(const p of ['index.html','styles.css','app.mjs','core.mjs','data/partners.json','data/manifest.json','data/aliases.json','data/screening.csv'])await copyFile(p,'dist/'+p);
console.log('Static app built. No external dependencies.');
