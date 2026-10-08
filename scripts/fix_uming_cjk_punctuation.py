"""Safely adjust U+3002 subset glyphs in embedded TrueType fonts without changing text content/metrics.

Only shifts the embedded UMingCN-0 glyph outlines for U+3002 and U+3001,
which otherwise render centered rather than in the lower left of an ideograph cell.
The fullstop text encoding, ToUnicode map and glyph advance are untouched.
"""
from __future__ import annotations
import argparse
import io
import re
import struct
from pathlib import Path
from collections import Counter
from hashlib import sha256
import fitz
from fontTools.ttLib import TTFont
DX, DY = -126, -182
ORIGINAL_BBOX = {'。':(387,263,637,513),'、':(386,279,640,506)}
PUNCT = {
  '3002': (-126, -182, '。'),
  '3001': (-140, -196, '、'),
}



def gettable(blob, name):
    num = struct.unpack_from('>H', blob,4)[0]
    for i in range(num):
        rec=12+16*i
        tag,checksum,offset,length=struct.unpack_from('>4sIII',blob,rec)
        if tag.decode()==name:return rec,offset,length
    raise RuntimeError('missing font table '+name)


def check_sum(raw):
    raw=raw+b'\0'*((-len(raw))%4)
    return sum(v[0] for v in struct.iter_unpack('>I',raw))&0xffffffff


def patch_ttf(ttf, glyph_index, dx=DX, dy=DY):
    raw=bytearray(ttf)
    grecord,glyfpos,glyflen=gettable(raw,'glyf')
    lrecord,locapos,localen=gettable(raw,'loca')
    _,headpos,_=gettable(raw,'head')
    locafmt=struct.unpack_from('>h',raw,headpos+50)[0]
    if locafmt==0:
        glyphstart,glyphend=[2*struct.unpack_from('>H',raw,locapos+2*x)[0] for x in [glyph_index,glyph_index+1]]
    elif locafmt==1:
        glyphstart,glyphend=[struct.unpack_from('>I',raw,locapos+4*x)[0] for x in [glyph_index,glyph_index+1]]
    else: raise RuntimeError('unexpected loca format')
    assert glyphend>glyphstart
    start=glyfpos+glyphstart
    cont=struct.unpack_from('>h',raw,start)[0]
    if cont<=0:raise RuntimeError('not a simple glyph')
    oldbbox=struct.unpack_from('>hhhh',raw,start+2)
    for i,val in enumerate(oldbbox):
        offset=dx if i%2==0 else dy
        struct.pack_into('>h',raw,start+2+2*i,val+offset)
    endpts=[struct.unpack_from('>H',raw,start+10+2*i)[0] for i in range(cont)]
    points=endpts[-1]+1
    ilenpos=start+10+2*cont
    instr_len=struct.unpack_from('>H',raw,ilenpos)[0]
    p=ilenpos+2+instr_len
    flags=[]
    while len(flags)<points:
        flag=raw[p];p+=1
        repeat=1
        if flag&0x08:
            repeat+=raw[p];p+=1
        flags.extend([flag]*repeat)
    assert len(flags)==points
    def coordwidth(flag,axis):
        short=0x02 if axis=='x' else 0x04
        same=0x10 if axis=='x' else 0x20
        return 1 if flag&short else 0 if flag&same else 2
    xstart=p
    ystart=p+sum(coordwidth(flag,'x') for flag in flags)
    assert coordwidth(flags[0],'x')==coordwidth(flags[0],'y')==2
    oldxy=struct.unpack_from('>h',raw,xstart)[0],struct.unpack_from('>h',raw,ystart)[0]
    struct.pack_into('>h',raw,xstart,oldxy[0]+dx)
    struct.pack_into('>h',raw,ystart,oldxy[1]+dy)
    assert glyphend<=glyflen
    struct.pack_into('>I',raw,grecord+4,check_sum(raw[glyfpos:glyfpos+glyflen]))
    struct.pack_into('>I',raw,headpos+8,0)
    struct.pack_into('>I',raw,headpos+8,(0xB1B0AFBA-check_sum(raw))&0xffffffff)
    diff=[i for i,(a,b) in enumerate(zip(ttf,raw)) if a!=b]
    assert len(raw)==len(ttf) and len(diff)<=24,('unbounded binary differences',len(diff))
    # independently parse to verify outline and all non-target glyph programs remain identical
    ft=TTFont(io.BytesIO(bytes(raw)))
    g=ft['glyf'][ft.getGlyphOrder()[glyph_index]]
    assert (g.xMin,g.yMin,g.xMax,g.yMax)==tuple(v+(dx if i%2==0 else dy) for i,v in enumerate(oldbbox))
    assert ft['head'].unitsPerEm==1024
    return bytes(raw),oldbbox,(g.xMin,g.yMin,g.xMax,g.yMax),len(diff)


def fonts_to_correct(doc):
    allfonts={f[0] for page in doc for f in page.get_fonts(full=True)}
    for fontxref in sorted(allfonts):
        ob=doc.xref_object(fontxref)
        if 'UMingCN-0' not in ob:continue
        m=re.search(r'/ToUnicode\s+(\d+)\s+0\s+R',ob)
        if not m:continue
        cmap=doc.xref_stream(int(m.group(1))).decode('latin1')
        font=TTFont(io.BytesIO(doc.extract_font(fontxref)[3]))
        target=[]
        for unicode_code,(dx,dy,char) in PUNCT.items():
            codes=re.findall(r'<([0-9A-Fa-f]{2,4})>\s+<'+unicode_code+'>',cmap)
            if not codes:continue
            assert len(codes)==1,(fontxref,char,codes)
            code=int(codes[0],16)
            glyphs={c.cmap[code] for c in font['cmap'].tables if code in c.cmap}
            assert len(glyphs)==1,(fontxref,char,glyphs)
            target.append((char,font.getGlyphID(next(iter(glyphs))),dx,dy))
        if not target:continue
        desc=int(re.search(r'/FontDescriptor\s+(\d+)\s+0\s+R',ob).group(1))
        fontfile=int(re.search(r'/FontFile2\s+(\d+)\s+0\s+R',doc.xref_object(desc)).group(1))
        yield fontxref,fontfile,target


def apply_to_doc(doc):
    changes=[]
    refs=list(fonts_to_correct(doc))
    assert len(refs)==18,('UMing punctuation subset count changed',len(refs))
    for fontxref,fontfile,targets in refs:
        patched=doc.xref_stream(fontfile)
        for char,gid,dx,dy in targets:
            patched,b0,b1,num=patch_ttf(patched,gid,dx,dy)
            if b0 != ORIGINAL_BBOX[char]:
                raise ValueError('Unexpected or already-shifted punctuation glyph for '+char)
            changes.append({'font_xref':fontxref,'fontfile_xref':fontfile,'character':char,
                            'glyph_index':gid,'dx':dx,'dy':dy,'before':b0,'after':b1,'bytes_modified':num})
        doc.update_stream(fontfile,patched)
    assert sum(c['character']=='。' for c in changes)==17
    assert sum(c['character']=='、' for c in changes)>0
    return changes


def run(path,out):
    doc=fitz.open(path)
    changes=apply_to_doc(doc)
    doc.save(out,garbage=0,deflate=True,no_new_id=True)
    doc.close()
    q=fitz.open(out)
    assert len(q)==299
    for row in changes:
        print(f"font={row['font_xref']} {row['character']} gid={row['glyph_index']} "
              f"before={row['before']} after={row['after']} mod_bytes={row['bytes_modified']}")
    print('total_glyphs',len(changes),'punct',Counter(c['character'] for c in changes))
    print('output',out,'size',Path(out).stat().st_size,'sha256',sha256(Path(out).read_bytes()).hexdigest())
    return changes

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');args=ap.parse_args()
    run(args.input,args.output)
