export const STAGES = ['Not reviewed','Shortlisted','Contacted','In conversation','Already known','Not a fit'];
export const activeStatuses = new Set(['RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION']);
export function statusLabel(s){return ({RECRUITING:'Recruiting',NOT_YET_RECRUITING:'Not yet recruiting',ACTIVE_NOT_RECRUITING:'Active, not recruiting',ENROLLING_BY_INVITATION:'Enrolling by invitation',COMPLETED:'Completed',TERMINATED:'Terminated',SUSPENDED:'Suspended',WITHDRAWN:'Withdrawn',UNKNOWN:'Status unknown',NOT_RECORDED:'Site status not recorded'})[s]||s;}
export function filterLeads(data,{tab='recent',query='',condition='',signal='',routes=false}={},work={}){
 const q=query.toLowerCase().trim();
 return data.leads.filter(l=> (tab!=='recent'||l.recent) && (tab!=='saved'||work[l.id]?.saved) && (!condition||l.conditions.includes(condition)) && (!signal||l.signals.includes(signal)) && (!routes||l.route) && (!q||[l.name,l.city,l.leadLine,l.route?.name,...l.facilities,...l.studyIds.map(id=>data.studies[id].title)].join(' ').toLowerCase().includes(q)));
}
export function cleanWork(input,data){
 if(!input||typeof input!=='object'||Array.isArray(input))return {};
 const output={};
 for(const l of data.leads){const w=input[l.id];if(w&&typeof w==='object')output[l.id]={saved:w.saved===true,stage:STAGES.includes(w.stage)?w.stage:'Not reviewed',note:typeof w.note==='string'?w.note.slice(0,4000):''};}
 return output;
}
export function csvCell(v){let s=String(v??'');if(/^[\s]*[=+@\-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}
export function exportCSV(data,leads,work={}){
 const header=['Lead','City','Conditions','Why consider','Suggested first question','Contact','Contact role','Contact type','Public email','Contact source','Contact checked','Latest study update','Study count','Study sources','Site statuses','Signals','Priority points','Relationship','Stage','Saved','Your notes','Snapshot date'];
 const rows=leads.map(l=>[l.name,l.city,l.conditions.join('; '),l.reason||l.leadLine||'Relevant UK study site in ClinicalTrials.gov',l.ask||'Establish the research owner and whether a wearable-validation discussion is relevant.',l.route?.name,l.route?.role,l.route?.kind,l.route?.email,l.route?.url,l.route?.checked,l.latest,l.studyIds.length,l.studyIds.map(n=>data.studies[n].url).join('; '),l.siteStatuses.map(s=>s.facility+': '+statusLabel(s.status)+' ('+s.study+')').join('; '),l.signals.join('; '),l.score,'Not publicly verified',work[l.id]?.stage||'Not reviewed',work[l.id]?.saved?'yes':'no',work[l.id]?.note||'',data.meta.retrievedAt.slice(0,10)]);
 return '\uFEFF'+[header,...rows].map(row=>row.map(csvCell).join(',')).join('\r\n');
}
export function makeBrief(data,l,work={}){
 const route=l.route;
 return [l.name,l.city,'Prepared for WombWise · snapshot '+data.meta.retrievedAt.slice(0,10),'', 'WHY CONSIDER',l.reason||'Named UK site in relevant endometriosis or PCOS studies. Confirm whether this team handles wearable-validation partnerships.','', 'SUGGESTED FIRST QUESTION',l.ask||'Who owns research partnerships, and is there interest in evaluating passive wearable signals alongside symptom measures?','', 'PUBLIC CONTACT ROUTE',route?`${route.name}\n${route.role}\n${route.email}\n${route.kind}\nSource: ${route.url}\nChecked: ${route.checked}`:'No institutional collaboration route verified. Use the linked study records to identify the investigator, then verify the right research office.','', 'STUDY EVIDENCE',...l.studyIds.map(n=>{const s=data.studies[n];const local=l.siteStatuses.filter(x=>x.study===n).map(x=>`${x.facility}: ${statusLabel(x.status)}`).join('; ');return `${s.title}\n${s.url}\nOverall: ${statusLabel(s.status)}; updated ${s.updated}\nUK site: ${local}`;}),'','RELATIONSHIP','Not publicly verified. Check WombWise’s existing contacts before approaching. Registry experience does not establish collaboration interest, capacity or data access.','', 'YOUR WORK', 'Stage: '+(work[l.id]?.stage||'Not reviewed'),work[l.id]?.note||'No notes.'].join('\n');
}
