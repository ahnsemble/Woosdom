"""PoC A: http_server=True 에셋 로딩 검증."""
import webview
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    window = webview.create_window(
        'PoC Test',
        url=os.path.join(SCRIPT_DIR, 'poc_index.html'),
        width=800, height=600,
    )
    webview.start(http_server=True)
