"""LEC08 폴더의 제출용 애니메이션 뷰어를 실행합니다."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    viewer = Path(__file__).resolve().parents[2] / 'LEC08' / 'animation_viewer.py'
    runpy.run_path(str(viewer), run_name='__main__')
