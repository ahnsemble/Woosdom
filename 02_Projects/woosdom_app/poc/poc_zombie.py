"""PoC C: 좀비 프로세스 방어.
macOS에서 psutil.net_connections()는 root 권한 필요 → lsof 대안 사용.
"""
import subprocess
import signal
import os


def kill_zombie_servers(port=23948):
    """지정 포트를 점유 중인 프로세스 정리 (lsof 기반, macOS 호환)."""
    killed = []
    try:
        result = subprocess.run(
            ['lsof', '-ti', f'tcp:{port}'],
            capture_output=True, text=True
        )
        pids = [int(p) for p in result.stdout.strip().split('\n') if p.strip()]
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
                print(f'  killed PID {pid}')
            except ProcessLookupError:
                pass
    except FileNotFoundError:
        print('[PoC C] lsof not found, using psutil fallback')
        import psutil
        for proc in psutil.process_iter(['pid', 'connections']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        proc.kill()
                        killed.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return killed


if __name__ == '__main__':
    result = kill_zombie_servers()
    print(f"정리된 프로세스: {result if result else '없음'}")
    print('[PoC C] psutil 좀비 정리 실행 성공')
