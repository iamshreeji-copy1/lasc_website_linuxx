"""Extract clean content blocks from the legacy product pages (tolerant of broken markup)."""
import re, os, json, glob
from html.parser import HTMLParser

def strip_comments(s): return re.sub(r'<!--.*?-->', '', s, flags=re.S)

class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks=[]; self.cur=None; self.in_heading=None; self.buf=[]
    def flush_text(self):
        t=re.sub(r'\s+',' ',''.join(self.buf)).strip()
        self.buf=[]
        if t: self.blocks.append(('text',t))
    def handle_starttag(self,tag,attrs):
        if tag in('h2','h3','h4','h5'):
            self.flush_text(); self.in_heading=tag
        elif tag in('p','ul','li','br','div'):
            self.flush_text()
    def handle_endtag(self,tag):
        if tag==self.in_heading:
            t=re.sub(r'\s+',' ',''.join(self.buf)).strip(); self.buf=[]
            if t: self.blocks.append((tag,t))
            self.in_heading=None
        elif tag in('p','ul','li','div') and not self.in_heading:
            self.flush_text()
        elif tag in('h2','h3','h4','h5') :
            # stray/mismatched closing heading: flush and keep going
            if self.in_heading: pass
            else: self.flush_text()
    def handle_data(self,d): self.buf.append(d)
    def close(self):
        super().close(); self.flush_text()

def extract(path):
    raw=strip_comments(open(path,encoding='utf-8',errors='replace').read())
    m=re.search(r'<div class="portfolio-description">(.*?)<div class="testimonial-item">',raw,re.S)
    desc=m.group(1) if m else ''
    b=Blocks(); b.feed(desc); b.close()
    # slides
    sl=re.search(r'<div class="swiper-wrapper[^>]*>(.*?)</div>\s*<div class="swiper-pagination',raw,re.S)
    imgs=re.findall(r'<img[^>]*src="([^"]+)"',sl.group(1)) if sl else []
    h1=re.search(r'<h2>([^<]+)</h2>',re.search(r'<section id="breadcrumbs".*?</section>',raw,re.S).group(0)) if re.search(r'<section id="breadcrumbs"',raw) else None
    return {'blocks':b.blocks,'imgs':imgs,'crumb':h1.group(1) if h1 else None,
            'has_testimonial':'testimonial-item' in raw}

if __name__=='__main__':
    out={}
    for f in sorted(glob.glob('portfolio-details-*.html')):
        out[f]=extract(f)
    json.dump(out,open('/tmp/claude-1000/-home-linux/7247eaf5-a22e-4a8c-9425-f30144325010/scratchpad/extract.json','w'),indent=1,ensure_ascii=False)
    for f,d in out.items():
        kinds=[k for k,_ in d['blocks']]
        print(f"{f}\n   crumb={d['crumb']!r} imgs={len(d['imgs'])} blocks={len(kinds)} seq={''.join({'h2':'T','h3':'S','h5':'I','text':'.','h4':'4'}[k] for k in kinds)}")
        for i in d['imgs']: print('      img',i, os.path.exists(i.replace('\\','/')))
