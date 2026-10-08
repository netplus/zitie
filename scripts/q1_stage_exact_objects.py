#!/usr/bin/env python3
"""Reconstruct exact, previously reviewed Q1 import bytes and stage unreferenced Git objects.

Temporary bridge. Does not change Git refs or claim release status. The transport
contains no source fonts; seven TTFont subsets are rebuilt from installed fonts.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,os,re,struct,subprocess,sys,tempfile,urllib.request,zlib
from pathlib import Path
from reportlab.pdfbase.ttfonts import TTFontFile
import fitz

ROOT=Path(__file__).resolve().parents[1]
RC1=ROOT/'deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf'
RC1_SHA='3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a'
TRANSFER_SHA='342e6cc61a93d65e337d54922b522c4b9d84aca18dd76601be263ced89a93c2a'
UNPACKED_SHA='79a6063d22d4c9057d21fbbed93c1ab410c21060ca0ff8b795c8005f7677f794'
MAIN_TREE='10b65a81a418713f720040285650f77af4b4d398'
EXPECTED_TREE='ac7aac8c4c07ae0969c7bbaee3a2edfefcb1d10d'

def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def git_sha(data:bytes)->str:return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def need(ok,msg):
 if not ok: raise ValueError(msg)

def normalize_pdf(raw:bytes)->bytes:
 parts=[b'PDFX1'];cursor=0
 for m in re.finditer(rb'\bstream\r?\n(.*?)\r?\nendstream\b',raw,re.S):
  body=m.group(1)
  try: un=zlib.decompress(body)
  except zlib.error:continue
  lv=next((i for i in (6,9,1,2,3,4,5,7,8,0) if zlib.compress(un,i)==body),None)
  if lv is None:continue
  prefix=raw[cursor:m.start(1)]
  parts.extend([b'R',struct.pack('>I',len(prefix)),prefix,b'Z',bytes([lv]),struct.pack('>I',len(un)),un])
  cursor=m.end(1)
 suffix=raw[cursor:];parts.extend([b'R',struct.pack('>I',len(suffix)),suffix])
 return b''.join(parts)

def make_seed():
 need(fitz.VersionBind=='1.26.7','PyMuPDF version mismatch; require 1.26.7')
 raw=RC1.read_bytes();need(sha256(raw)==RC1_SHA,'RC1 original bytes changed')
 doc=fitz.open(stream=raw,filetype='pdf')
 for page in doc:
  page.add_redact_annot(fitz.Rect(0,page.rect.height-30,page.rect.width,page.rect.height),fill=(1,1,1))
  page.apply_redactions(images=0,graphics=0,text=0)
 result=doc.tobytes(garbage=4,deflate=True,no_new_id=True)
 return normalize_pdf(result)

def unpack_stream(raw:bytes,recipes:dict)->list:
 pos=0;results=[];subset_cache={}
 def read_font(key):
  if key not in subset_cache:
   rec=recipes[key]
   font_file=Path(rec['font_file'])
   need(font_file.is_file(),'Missing installed font: '+str(font_file))
   font=TTFontFile(str(font_file)).makeSubset(rec['subset'])
   need(sha256(font)==key,'Font subset mismatch: '+key)
   subset_cache[key]=font
  return subset_cache[key]
 def restore_pdf(encoded):
  need(encoded[:5]==b'PDFX2','Bad PDFX2 record')
  p=5;parts=[]
  while p<len(encoded):
   tag=encoded[p:p+1];p+=1
   if tag==b'F':
    lv=encoded[p];p+=1;key=encoded[p:p+32].hex();p+=32
    need(key in recipes,'Missing font recipe: '+key)
    parts.append(zlib.compress(read_font(key),lv));continue
   lv=None
   if tag==b'Z':lv=encoded[p];p+=1
   need(tag in (b'R',b'Z'),'Unknown PDFX2 tag')
   n=struct.unpack('>I',encoded[p:p+4])[0];p+=4
   b=encoded[p:p+n];p+=n
   parts.append(b if tag==b'R' else zlib.compress(b,lv))
  return b''.join(parts)
 while pos<len(raw):
  need(pos+4<=len(raw),'Truncated transport header')
  n=struct.unpack('>I',raw[pos:pos+4])[0];pos+=4
  meta=json.loads(raw[pos:pos+n]);pos+=n
  relative=Path(meta['path'])
  need(not relative.is_absolute() and '..' not in relative.parts,'Unsafe target path')
  length=meta['length'];payload=raw[pos:pos+length];pos+=length
  need(len(payload)==length,'Truncated payload')
  content=restore_pdf(payload) if meta['pdfx'] else payload
  need(sha256(content)==meta['sha256'],'SHA256 mismatch: '+str(relative))
  need(git_sha(content)==meta['sha'],'Git object mismatch: '+str(relative))
  results.append((relative.as_posix(),content,meta['sha']))
 need(pos==len(raw) and len(results)==25,'Unexpected transport record count')
 return results

def post_git(resource,body,token):
 url='https://api.github.com/repos/netplus/zitie/git/'+resource
 payload=json.dumps(body,separators=(',',':')).encode()
 req=urllib.request.Request(url,data=payload,headers={'Accept':'application/vnd.github+json','Content-Type':'application/json','Authorization':'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28'})
 with urllib.request.urlopen(req,timeout=90) as resp:return json.load(resp)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');args=p.parse_args()
 source=ROOT/'.github/q1-transport/payload.txt'
 text=source.read_text('ascii')
 entries=text.splitlines()
 need(len(entries)==80,'Transport part count mismatch')
 compressed=b''
 for i,s in enumerate(entries):
  prefix,sep,fragment=s.partition(':')
  need(bool(sep) and prefix==f'{i:03d}','Out-of-order transport fragment')
  compressed+=base64.b64decode(fragment,validate=True)
 need(sha256(compressed)==TRANSFER_SHA,'Compressed transport changed')
 zstd_payload=zlib.decompress(compressed)
 recipes=json.loads((ROOT/'.github/q1-transport/font-recipes.json').read_text())
 seed=make_seed()
 with tempfile.TemporaryDirectory(prefix='q1-import-') as tmp:
  d=Path(tmp);(d/'seed.raw').write_bytes(seed);(d/'compressed.zst').write_bytes(zstd_payload)
  subprocess.run(['zstd','-q','-d','-f','-D',str(d/'seed.raw'),str(d/'compressed.zst'),'-o',str(d/'transport.raw')],check=True)
  unpacked=(d/'transport.raw').read_bytes()
 need(sha256(unpacked)==UNPACKED_SHA,'Unpacked transport checksum mismatch')
 results=unpack_stream(unpacked,recipes)
 audit={'source':'Q1 locally reviewed RC2/RC3 handoff','transport_sha256':TRANSFER_SHA,'count':len(results),'target_tree':EXPECTED_TREE,
        'entries':[{'path':name,'sha':sha,'bytes':len(content),'sha256':sha256(content)} for name,content,sha in results],
        'staged':False,'refs_modified':False,'release_granted':False}
 if args.stage:
  need(os.getenv('GITHUB_REF')=='refs/heads/maintenance/q1-rc3-stage-20261008','Staging allowed only on exact temporary branch')
  token=os.getenv('GH_TOKEN');need(token,'GITHUB_TOKEN unavailable')
  tree=[]
  for name,content,sha in results:
   blob=post_git('blobs',{'content':base64.b64encode(content).decode('ascii'),'encoding':'base64'},token)
   need(blob.get('sha')==sha,'GitHub returned mismatched SHA for '+name)
   tree.append({'path':name,'mode':'100644','type':'blob','sha':sha})
  made=post_git('trees',{'base_tree':MAIN_TREE,'tree':tree},token)
  need(made.get('sha')==EXPECTED_TREE,'GitHub tree mismatch')
  audit['staged']=True
 out=ROOT/'build/q1-stage';out.mkdir(parents=True,exist_ok=True)
 (out/'q1-stage-report.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'staged':audit['staged'],'count':audit['count'],'tree':EXPECTED_TREE,'refs_modified':False}))

if __name__=='__main__':
 try:main()
 except Exception as e:
  print(type(e).__name__+': '+str(e),file=sys.stderr);raise
