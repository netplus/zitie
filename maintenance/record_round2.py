#!/usr/bin/env python3
"""One-time transcription of the documented 2026-09-29 review, not an automatic review."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def save(p,x):
    (R/p).parent.mkdir(parents=True,exist_ok=True)
    (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    b=load('data/B01.json')
    if b['version']=='0.2.0-draft':
        raise SystemExit('Already applied; refusing to replace subsequent editorial changes.')
    cat=load('sources/catalog.json')
    sources=[
      ('S04','现代汉语通用字笔顺规范','1997-STROKE-ORDER','国家语言文字工作委员会标准化工作委员会编；语文出版社，1997年8月第1版','9996a58e3f515d307bf35e104cf624a84f876d5e','ca8a0139744cf8105cb7e4ae7464ebc68cb76310b5a29e7cf004b2489a35ae65',458,[1,2,4,5,6,7,8,10,12,14,15,19,20]),
      ('S05','GB13000.1字符集汉字折笔规范','GF2001—2001','教育部、国家语委','d9802042adae66ec106a7b977d019341a0492aa6','68a1420580a7eedde79eeb55b91b6b2ff10ef9155d98633ccc712838f04e9b14',9,[1,4,5,6,7,8,9]),
      ('S06','汉语国际教育用音节汉字词汇等级划分','GF0015—2010','教育部、国家语委','13c76ed4c0dd835d356dd2c4c0504e050a576061','0d647e1378847480364e2603030fe6aa6102d99320c42cac631b2fb3155d18ce',157,[1,3,7,31,34,37,42,43,46,47,49,52,74]),
      ('S07','现代常用独体字规范','GF0013—2009','教育部、国家语委','0487d736363e6102faac0a1ed3c7f422f323f1ad','eeedf11ca7e0e38c2a79283c5b9e200fbec011c87c1fa24536045518ab94e5a7',7,[1,5,6]),
      ('S03','现代常用字部件及部件名称规范','GF0014—2009','教育部、国家语委','bb3923a5cab4c344217418b0ee4bebb548271bc6','bb554d91ac39dc10470e3186555ca1140c150b678190f63624ecf6f2298dffc6',41,[1,2,3,4,5,6,7,9])]
    for sid,title,pub,publisher,blob,sha,pages,checked in sources:
        item={'id':sid,'title':title,'publication_id':pub,'publisher':publisher,'status':'formal_scan_acquired_selected_pages_reviewed','urls':['https://api.github.com/repos/zispace/hanzi-docs/git/blobs/'+blob],'sha256':sha,'git_blob_sha':blob,'pdf_pages':pages,'reviewed_pdf_pages':checked,'checked_at':'2026-09-29','provenance':'原出版物扫描件由zispace/hanzi-docs托管；版本身份据实际原件核查，平台不是规范发布者。','limits':'仅支持实际审读的页面与字段，不声明独立编制或独立双人审稿。'}
        if sid=='S04':item.update(isbn='7-80126-201-8',limits='2020版明确继承1997版；按不同出版物交叉检查，不按独立证据体系计数。说明第2页与正文第2页须区分。')
        if sid=='S06':item['limits']='仅引用词条读音，不采用旧版词汇等级作为当前教学分级。工、巾取工人、毛巾的语素读音，并非独立字条。'
        cat['sources']=[s for s in cat['sources'] if s['id']!=sid]+[item]
    cat['as_of']='2026-09-29';save('sources/catalog.json',cat)
    b.update(version='0.2.0-draft',status='content_cross_checked_scope_pending',metadata_review='passed',metadata_review_record='reviews/B01-cross.md',release_eligible=False,remaining_gates=['GF0011—2022全文及目标版主项身份核验'],draft_label='编写稿｜本批笔顺、笔名及读音已核；2022版主表范围待核。')
    b['cross_review']={'status':'passed','source_id':'S04','publication_id':'1997-STROKE-ORDER','reviewer':'ChatGPT','date':'2026-09-29','fields':['stroke_count','stroke_order'],'pdf_pages':[6,7,8],'printed_pages':[1,2,3],'method':'实际打开1997版跟随式与笔画式图，对照2020版原图及JSON顺序；不仅比较类别码。','limits':'两个不同出版物属于同一规范沿革；不是独立专家审定。'}
    b['layout_review']={'status':'pending','reviewer':None,'note':'脚注和前言改变，等待v0.2逐页检查。'}
    pron={'一':(52,46,1897,'一','yī','direct'),'十':(47,41,1446,'十','shí','direct'),'人':(46,40,1348,'人','rén','direct'),'八':(31,25,13,'八','bā','direct'),'大':(34,28,276,'大','dà','direct'),'工':(37,31,553,'工人','gōng·rén','morpheme_first'),'土':(49,43,1639,'土','tǔ','direct'),'口':(42,36,968,'口','kǒu','direct'),'山':(46,40,1385,'山','shān','direct'),'巾':(74,68,1550,'毛巾','máojīn','morpheme_last')}
    for e in b['entries']:
        ch=e['character'];pn=6 if ch in '一十人八' else (7 if ch in '大工土' else 8)
        e['cross_evidence']={'source_id':'S04','pdf_page':pn,'printed_page':pn-5,'fields':['stroke_count','stroke_order'],'result':'matched'}
        pp,printed,num,word,py,method=pron[ch]
        e['pronunciation_evidence']={'source_id':'S06','pdf_page':pp,'printed_page':printed,'word_id':num,'level':2 if ch=='巾' else 1,'word':word,'printed_pinyin':py,'application':method,'adopted_pinyin':e['pinyin'],'result':'matched'}
        e['structure_evidence']={'source_id':'S07','pdf_page':5,'printed_page':2,'table':'现代常用独体字表','result':'listed'}
        e['stroke_name_evidence']=[{'source_id':'S04','pdf_page':5,'printed_page_label':'说明第2页','supports':'横、竖、撇及捺／竖钩与类别码的关系；按实际笔形区分，不把4一律读为捺。'}]
        if ch in '口山巾':e['stroke_name_evidence'].append({'source_id':'S05','pdf_page':9 if ch=='巾' else 8,'printed_page':7 if ch=='巾' else 6,'table_row':{'口':'5.1','山':'5.4','巾':'5.15'}[ch],'adopted_name':{'口':'横折','山':'竖折','巾':'横折钩'}[ch]})
    save('data/B01.json',b)
    chars='水火木日月田目手牛毛'
    names=['竖钩 横撇 撇 捺','点 撇 撇 捺','横 竖 撇 捺','竖 横折 横 横','撇 横折钩 横 横','竖 横折 横 竖 横','竖 横折 横 横 横','撇 横 横 竖钩','撇 横 横 竖','撇 横 横 竖弯钩']
    codes=['2534','4334','1234','2511','3511','25121','25111','3112','3112','3115'];py=['shuǐ','huǒ','mù','rì','yuè','tián','mù','shǒu','niú','máo'];primary=[14,16,12,13,15,20,19,14,14,14];second=[12,15,10,12,14,20,19,12,12,12]
    tips=[('先中间，再左边，最后写右边。','第2笔横撇一笔写完，不拆成两笔。','竖钩居中；右边的撇和捺分两笔写。'),('先左点，再右上短撇，再写长撇。','第2笔是撇，不是再写一个点。','两撇先后分清，最后一捺舒展。'),('先横后竖，再写撇和捺。','这一页练独体木，末笔是捺。','横竖相交；撇捺向两边伸展。'),('先左竖、横折，再写两横。','里面的横先写，最下面的横最后写。','共4笔；横折不拆笔，最后封口。'),('先撇、横折钩，再写里面两横。','这里练独体月，不照搬日的起笔。','第1笔是撇，第2笔的钩不遗漏。'),('先搭外框，再写里面的横和竖。','第5笔才写底横，不能先封口。','中间先横后竖；最后写底横。'),('先左竖、横折，再写三横。','里面两横先写，最后一横封口。','共5笔；里面两横不漏写。'),('先短撇，再写两横，最后竖钩。','第1笔是撇，不是横。','末笔竖钩居中；两横先后不颠倒。'),('先撇、两横，再写中间的竖。','独体牛最后写竖；牛字旁另页学。','第3笔是横，第4笔才是竖。'),('先撇、两横，最后竖弯钩。','末笔从竖到弯、到钩，连续写完。','两横写完再落末笔，不把弯钩拆开。')]
    x={'batch_id':'B02','version':'0.2.0-draft','status':'stroke_order_cross_checked_metadata_pending','scope_source':'S01-2009','primary_source':'S02','primary_review':{'reviewer':'ChatGPT','date':'2026-09-29','method':'实际查看10字完整跟随式行，保留物理页和原印页映射。','pdf_pages':sorted(set(primary)),'sha256':b['primary_review']['sha256']},'cross_review':{'status':'passed','source_id':'S04','reviewer':'ChatGPT','date':'2026-09-29','fields':['stroke_count','stroke_order'],'pdf_pages':sorted(set(second)),'limits':'与S02属于同一规范沿革，不作为独立统计证据。'},'metadata_review':'fine_names_mapped_pronunciation_completion_pending','artwork_review':{'status':'pending','reviewer':None},'layout_review':{'status':'pending','reviewer':None},'release_eligible':False,'remaining_gates':['读音逐项证据','GF0011—2022全文及目标版主项身份核验','本版图形与页面检查'],'draft_label':'编写稿｜两部规范笔顺图已核；读音等字段仍待复核。','entries':[]}
    for g,ns,code,pin,pn,ss,t in zip(chars,names,codes,py,primary,second,tips):
        x['entries'].append({'character':g,'pinyin':pin,'stroke_names':ns.split(),'order_code':code,'primary_pdf_page':pn,'primary_printed_page':pn-6,'cross_evidence':{'source_id':'S04','pdf_page':ss,'printed_page':ss-5,'fields':['stroke_count','stroke_order'],'result':'matched'},'structure_evidence':{'source_id':'S07','pdf_page':6 if g in '田目' else 5,'printed_page':3 if g in '田目' else 2,'result':'listed'},'tips':t[:2],'check':t[2]})
    save('data/B02.json',x)
    bs=load('data/batches.json');bs['frozen_batches'][0]['status']=b['status'];bs['frozen_batches'][1]['status']=x['status'];save('data/batches.json',bs)
if __name__=='__main__':main()
