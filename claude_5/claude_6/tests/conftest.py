"""pytest 公共夹具。"""

from __future__ import annotations

import sys
from pathlib import Path

# 将 src 加入 import 路径，便于未安装时直接运行测试
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
