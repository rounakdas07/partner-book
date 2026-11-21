import urllib.request,urllib.parse,json,time,hashlib,datetime,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
query='Endometriosis OR "Polycystic Ovary Syndrome"'
params={'query.cond':query,'pageSize':1000,'countTotal':'true','format':'json'}
records=[];requests=[];page=0
while True:
 url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params)
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=55) as r: raw=r.read()
   break
  except Exception:
   if attempt==2: raise
   time.sleep(2)
 data=json.loads(raw);page+=1
 requests.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'records':len(data['studies'])})
 records.extend(data['studies']);print('Page',page,'records',len(records),'of',data.get('totalCount'),flush=True)
 if not data.get('nextPageToken'):break
 params['pageToken']=data['nextPageToken']
ids=[x['protocolSection']['identificationModule']['nctId'] for x in records]
assert len(ids)==len(set(ids))
(root/'data/registry-raw.json').write_text(json.dumps(records,separators=(',',':')))
manifest={'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':query,'recordCount':len(records),'requests':requests,'api':'https://clinicaltrials.gov/api/v2/studies','source':'ClinicalTrials.gov','searchUrl':'https://clinicaltrials.gov/search?cond='+urllib.parse.quote(query)}
(root/'data/manifest.json').write_text(json.dumps(manifest,indent=2))
uk=[r for r in records if any(l.get('country')=='United Kingdom' for l in r['protocolSection'].get('contactsLocationsModule',{}).get('locations',[]))]
(root/'data/uk-raw.json').write_text(json.dumps(uk,indent=2))
print('UK studies',len(uk),flush=True)
