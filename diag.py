from playwright.sync_api import sync_playwright
import sys, json
QA=""":root{--f-display:'Liberation Sans Narrow','DejaVu Sans Condensed',sans-serif !important;
--f-script:'Carlito',cursive !important;--f-ui:'Inter',sans-serif !important;
--f-body:'Roboto',sans-serif !important;--f-label:'Inter',sans-serif !important;}"""
page=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto(f'file:///home/claude/sojo/dist/{page}.html', wait_until='load')
    pg.add_style_tag(content=QA); pg.wait_for_timeout(700)
    total=pg.evaluate("document.body.scrollHeight")
    imgs=pg.evaluate("""() => {
      let a=0, n=0;
      document.querySelectorAll('main img').forEach(i=>{const r=i.getBoundingClientRect(); if(r.height>10){a+=r.height;n++;}});
      const secs=[...document.querySelectorAll('main > section')].map(s=>{
        const r=s.getBoundingClientRect();
        const eb=s.querySelector('.eyebrow,.crumb'); const h=s.querySelector('h1,h2');
        return {h:Math.round(r.height), label:((eb?eb.textContent:'')+' / '+(h?h.textContent:'')).replace(/\\s+/g,' ').trim().slice(0,48)};
      });
      return {imgArea:Math.round(a), imgCount:n, secs};
    }""")
    print(f"{page}: total {total}px  |  images {imgs['imgCount']} occupying {imgs['imgArea']}px ({round(100*imgs['imgArea']/total)}% of page)")
    for s in sorted(imgs['secs'], key=lambda x:-x['h'])[:6]:
        print(f"    {s['h']:>6}px  {s['label']}")
    b.close()
