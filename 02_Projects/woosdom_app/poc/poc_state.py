"""PoC B: window.state 이벤트 검증. (PyWebView 6.0+)"""
import webview
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def update_state(window):
    time.sleep(3)
    window.state.counter = 1
    print('[PoC B] counter = 1')
    time.sleep(2)
    window.state.counter = 2
    print('[PoC B] counter = 2')
    time.sleep(2)
    window.state.message = 'Hello from Python'
    print('[PoC B] message set')


if __name__ == '__main__':
    window = webview.create_window(
        'State PoC',
        url=os.path.join(SCRIPT_DIR, 'poc_state.html'),
        width=600, height=400,
    )
    webview.start(func=update_state, args=(window,), http_server=True)
