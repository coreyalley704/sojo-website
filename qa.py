from playwright.sync_api import sync_playwright
import sys
QA="""<style>
:root{--f-display:'Liberation Sans Narrow','DejaVu Sans Condensed',sans-serif !important;
--f-script:'Carlito',cursive !important;--f-ui:'Inter',sans-serif !important;
--f-body:'Roboto',sans-serif !important;--f-label:'Inter',sans-serif !important;--f-mono:'Inter',sans-serif !important;}
.script{font-style:italic}
</style>"""
pages=sys.argv[1:] or ['index']
with sync_playwright() as p:
    b=p.chromium.launch(args=['--font-render-hinting=none'])
    for name in pages:
        for w,h,tag in ((1440,1000,'d'),(390,844,'m')):
            pg=b.new_page(viewport={'width':w,'height':h}, device_scale_factor=1)
            pg.goto(f'file:///home/claude/sojo/dist/{name}.html', wait_until='load')
            pg.add_style_tag(content=QA.replace('<style>','').replace('</style>',''))
            pg.wait_for_timeout(900)
            for i in range(30): pg.mouse.wheel(0,700); pg.wait_for_timeout(60)
            pg.wait_for_timeout(600); pg.mouse.wheel(0,-40000); pg.wait_for_timeout(400)
            pg.screenshot(path=f'/home/claude/sojo/qa-{name}-{tag}.png', full_page=True)
            pg.close()
    b.close()
print('done')
