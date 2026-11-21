"""Screen the complete registry pull and consolidate explicit UK site aliases.
No external packages. Re-run fetch_registry.py first to refresh the snapshot.
"""
import csv, datetime, hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
ACTIVE={'RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION'}
GROUPS={
 'edinburgh':('Edinburgh endometriosis research','Edinburgh',[
  'Royal Infirmary of Edinburgh','University of Edinburgh','Centre for Reproductive Health, Institute for Regeneration and Repair, University of Edinburgh','Institute for Regeneration and Repair, University of Edinburgh and Royal Infirmary of Edinburgh']),
 'oxford':('Oxford EndoCaRe & reproductive health','Oxford',[
  'NDOG, University of Oxford','Oxford University Hospitals Foundation Trust','University of Oxford','John Radcliffe Hospital',"Nuffield Department Women's and Reproductive Health"]),
 'birmingham':('Birmingham PCOS research','Birmingham',['Institute of Metabolism and Systems Research','Wellcome Trust Clinical Research Facility']),
 'chelsea':('Chelsea and Westminster','London',['Chelsea and Westminster Hospital NHS Foundation Trust','Chelsea and Westminster NHS Foundation Trust']),
 'hull':('Hull diabetes & endocrinology research','Hull',['Michael White Centre for Diabetes and Endocrinology','Hull University Teaching Hospitals NHS Trust','Hull University Teaching Hospitals NHS Trust, Academic diabetes, Endocrinology and metabolism','Hull & East Yorkshire Hospitals NHS Trust']),
 'sheffield':('Sheffield Teaching Hospitals','Sheffield',['Academic Unit of Reproductive and Developmental Medicine, Jessop Wing, Tree Root Walk','Royal Hallamshire Hospital','Sheffield Teaching Hospitals NHS Trust, Jessop Wing','Jessop Wing, Sheffield Teaching Hospitals NHS Foundation Trust']),
 'liverpool':("Liverpool Women's Hospital",'Liverpool',['Liverpool Women Hospital','Liverpool Womens Hospital']),
 'norwich':('Norfolk and Norwich University Hospitals','Norwich',['Norfolk and Norwich Hospital','Norfolk and Norwich University Hospital - Norfolk and Norwich University Hospitals NHS Foundation Trust']),
 'accellacare':('Accellacare UK research sites','Multiple UK cities',['Accellacare Yorkshire','Accellacare Northamptonshire','Accellacare Warwickshire','Accellacare North London','Accellacare South London']),
}
# These are descriptive research clusters, not legal-entity mergers.
ALIASES={name:key for key,(_,_,names) in GROUPS.items() for name in names}
DIGITAL=re.compile(r'\b(?:smartwatch(?:es)?|wearables?|actigraph(?:y|ic)?|acceleromet(?:er|ers|ry)|fitbit|oura)\b',re.I)
DIARY=re.compile(r'\b(?:diary|diaries|smartphone(?:s)?|mobile app|symptom tracking)\b',re.I)

def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def flatten(v):
 if isinstance(v,dict):return ' '.join(flatten(x) for x in v.values())
 if isinstance(v,list):return ' '.join(flatten(x) for x in v)
 return str(v)
def signal(p,regex,label):
 for field in ['descriptionModule','outcomesModule']:
  text=flatten(p.get(field,{}));m=regex.search(text)
  if m:return {'label':label,'term':m.group(),'field':field}
 return None

def prepare():
 raw=json.loads((DATA/'registry-raw.json').read_text());manifest=json.loads((DATA/'manifest.json').read_text())
 asof=datetime.date.fromisoformat(manifest['retrievedAt'][:10]);cutoff=(asof.replace(year=asof.year-2)).isoformat()
 groups={};studies={};excluded=[];location_count=0
 with (DATA/'screening.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['nct_id','title','uk_site_present','countries','source'])
  for r in raw:
   p=r['protocolSection'];i=p['identificationModule'];n=i['nctId'];locs=p.get('contactsLocationsModule',{}).get('locations',[])
   uk=[l for l in locs if l.get('country')=='United Kingdom'];url='https://clinicaltrials.gov/study/'+n
   writer.writerow([n,i['briefTitle'],'yes' if uk else 'no','; '.join(sorted({l.get('country','Not recorded') for l in locs})),url])
   if not uk:continue
   status=p['statusModule'];updated=status['lastUpdatePostDateStruct']['date'];design=p.get('designModule',{})
   conditions=p.get('conditionsModule',{}).get('conditions',[]);condtext=' '.join(conditions).lower()
   conditions_normal=[]
   if 'endometri' in condtext:conditions_normal.append('Endometriosis')
   if any(x in condtext for x in ['polycystic','pcos']):conditions_normal.append('PCOS')
   if not conditions_normal:conditions_normal=['Other / related']
   signals=[x for x in [signal(p,DIGITAL,'Wearable data'),signal(p,DIARY,'Symptoms / diaries')] if x]
   if design.get('studyType')=='OBSERVATIONAL':signals.append({'label':'Observational study','term':'OBSERVATIONAL','field':'designModule.studyType'})
   studies[n]={'id':n,'title':i['briefTitle'],'url':url,'status':status['overallStatus'],'updated':updated,'verified':status.get('statusVerifiedDate',''),'conditions':conditions_normal,'rawConditions':conditions,'type':design.get('studyType','Not recorded'),'signals':signals,'sponsor':p.get('sponsorCollaboratorsModule',{}).get('leadSponsor',{}).get('name','Not recorded'),'enrollment':design.get('enrollmentInfo',{}),'locations':[]}
   for loc in uk:
    location_count+=1;name=loc.get('facility','').strip();city=loc.get('city','Not recorded')
    if not name or re.match(r'^(Site:|Research Site$)',name,re.I):
     excluded.append({'study':n,'facility':name or 'Not named','city':city,'reason':'No identifiable organisation'});continue
    key=ALIASES.get(name,slug(name+' '+city));display,basecity,_=GROUPS.get(key,(name,city,[]))
    if key not in groups:groups[key]={'id':key,'name':display,'city':basecity,'facilities':[],'studyIds':[],'siteStatuses':[]}
    g=groups[key]
    if name not in g['facilities']:g['facilities'].append(name)
    if n not in g['studyIds']:g['studyIds'].append(n)
    g['siteStatuses'].append({'study':n,'status':loc.get('status','NOT_RECORDED'),'facility':name})
    studies[n]['locations'].append({'group':key,'facility':name,'city':city,'status':loc.get('status','NOT_RECORDED')})
 for g in groups.values():
  ss=[studies[n] for n in g['studyIds']];g['studyIds'].sort(key=lambda n:studies[n]['updated'],reverse=True)
  g['latest']=max(s['updated'] for s in ss);g['recent']=g['latest']>=cutoff
  g['conditions']=sorted({c for s in ss for c in s['conditions']})
  g['signals']=sorted({x['label'] for s in ss for x in s['signals']})
  # "Current" requires a recent study update AND the site's own active status.
  # An overall recruiting trial does not establish that its UK site is open.
  g['currentStudyIds']=sorted({x['study'] for x in g['siteStatuses'] if x['status'] in ACTIVE and studies[x['study']]['updated']>=cutoff})
  g['recentStudyIds']=[s['id'] for s in ss if s['updated']>=cutoff]
  g['score']=(40 if g['currentStudyIds'] else 0)+(20 if g['recent'] else 0)+(20 if 'Wearable data' in g['signals'] else 0)+(10 if 'Symptoms / diaries' in g['signals'] else 0)+(10 if 'Observational study' in g['signals'] else 0)
 enrichment=json.loads((DATA/'enrichment.json').read_text()) if (DATA/'enrichment.json').exists() else {}
 for g in groups.values():
  g.update(enrichment.get(g['id'],{}))
  if g.get('route'):g['score']+=15
 ordered=sorted(groups.values(),key=lambda g:(-g['score'],-int(g['latest'].replace('-','')),g['name']))
 out={'meta':{**manifest,'recentCutoff':cutoff,'ukStudyCount':len(studies),'ukLocationRows':location_count,'excludedLocationRows':len(excluded),'leadCount':len(ordered),'recentLeadCount':sum(g['recent'] for g in ordered),'namedUKStudyCount':sum(bool(s['locations']) for s in studies.values()),'currentLeadCount':sum(bool(g['currentStudyIds']) for g in ordered),'screeningSha256':hashlib.sha256((DATA/'screening.csv').read_bytes()).hexdigest()},'leads':ordered,'studies':studies,'excluded':excluded}
 (DATA/'partners.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
 (DATA/'aliases.json').write_text(json.dumps(GROUPS,indent=2))
 print(json.dumps({k:out['meta'][k] for k in ['recordCount','ukStudyCount','ukLocationRows','excludedLocationRows','leadCount','recentLeadCount','currentLeadCount']}))
 print([(g['id'],g['score'],g['latest']) for g in ordered[:12]])
if __name__=='__main__':prepare()
