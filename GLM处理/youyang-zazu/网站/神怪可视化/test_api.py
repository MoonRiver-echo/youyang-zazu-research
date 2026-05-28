#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

r = urllib.request.urlopen('http://localhost:8890/api/stories')
stories = json.loads(r.read().decode('utf-8'))
print("=== STORIES ===")
print("Count:", len(stories))
for s in stories:
    pid = s.get('pid','')
    title = s.get('title','')
    at = s.get('annotated_text','')
    ann = s.get('annotations',[])
    ot = s.get('original_text','')
    print(f"  {pid}: title='{title}'")
    print(f"    annotated_text length: {len(at)}")
    print(f"    annotations count: {len(ann)}")
    print(f"    original_text length: {len(ot)}")
    if len(at) > 0:
        print(f"    annotated_text prefix: {at[:100]}")
    if len(ann) > 0:
        print(f"    first annotation: {ann[0]}")

r2 = urllib.request.urlopen('http://localhost:8890/api/stats')
stats = json.loads(r2.read().decode('utf-8'))
print("\n=== STATS ===")
print("Keys:", list(stats.keys()))
ns = stats.get('narrative_stats',[])
print("narrative_stats count:", len(ns))
if len(ns) > 0:
    print("First narr stat:", ns[0])
kf = stats.get('keyword_frequency',[])
print("keyword_frequency count:", len(kf))