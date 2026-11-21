import json,pathlib,sys,unittest,importlib.util,collections,csv,hashlib,io
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prep',root/'scripts/prepare_data.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
d=json.loads((root/'data/partners.json').read_text());raw=json.loads((root/'data/registry-raw.json').read_text());byid={r['protocolSection']['identificationModule']['nctId']:r['protocolSection'] for r in raw}
class DataTests(unittest.TestCase):
 def test_screening_complete(self):
  rows=list(csv.DictReader(io.StringIO((root/'data/screening.csv').read_text())));self.assertEqual(len(rows),len(raw));self.assertEqual({r['nct_id'] for r in rows},set(byid));self.assertEqual(d['meta']['screeningSha256'],hashlib.sha256((root/'data/screening.csv').read_bytes()).hexdigest())
 def test_every_lead_comes_from_explicit_uk_location(self):
  for l in d['leads']:
   self.assertEqual(len(l['studyIds']),len(set(l['studyIds'])))
   for n in l['studyIds']:
    names={x.get('facility') for x in byid[n]['contactsLocationsModule']['locations'] if x.get('country')=='United Kingdom'}
    self.assertTrue(set(l['facilities'])&names)
 def test_current_sites_not_inferred_from_trial_status(self):
  for l in d['leads']:
   expected={s['study'] for s in l['siteStatuses'] if s['status'] in prep.ACTIVE and d['studies'][s['study']]['updated']>=d['meta']['recentCutoff']}
   self.assertEqual(set(l['currentStudyIds']),expected)
 def test_keyword_false_positives(self):
  self.assertIsNone(prep.DIGITAL.search('behavioural encouraged'))
  for text in ['smartwatch','smartwatches','accelerometer','wearable','Oura']:
   self.assertIsNotNone(prep.DIGITAL.search(text))
 def test_counts_and_exclusions_reconcile(self):
  included=sum(len(s['locations']) for s in d['studies'].values())
  self.assertEqual(included+len(d['excluded']),d['meta']['ukLocationRows'])
  self.assertEqual(sum(l['recent'] for l in d['leads']),d['meta']['recentLeadCount'])
  self.assertEqual(len(d['leads']),d['meta']['leadCount'])
  self.assertEqual(len(d['studies']),d['meta']['ukStudyCount'])
 def test_dates_and_contact_sources(self):
  for l in d['leads']:
   self.assertEqual(l['latest'],max(d['studies'][n]['updated'] for n in l['studyIds']))
   if l.get('route'):self.assertTrue(l['route']['url'].startswith('https://'));self.assertIn('@',l['route']['email'])
if __name__=='__main__':unittest.main()
