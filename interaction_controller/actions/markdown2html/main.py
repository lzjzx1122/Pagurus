import markdown
import base64
import time


start = time.time()

def md2html(mdstr):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']

    html = '''
    <html lang="zh-cn">
    <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    <link href="default.css" rel="stylesheet">
    <link href="github.css" rel="stylesheet">
    </head>
    <body>
    %s
    </body>
    </html>
    '''

    ret = markdown.markdown(mdstr,extensions=exts)
    return html % ret

def main(params):
    with open('/proxy/exec/markdown2html/example.md', 'r') as f:
        text = f.read()

        print({"html_response": md2html(text)})

    print('latency:', time.time() - start)

