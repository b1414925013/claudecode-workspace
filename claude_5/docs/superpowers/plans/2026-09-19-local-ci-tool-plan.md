# 本地 CI 工具（CI Runner）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本机建立一个用户态运行、零新增依赖的轻量 CI 工具，提供多任务管理、网页配置步骤、手动/cron 触发、实时构建日志、构建历史和桌面通知。

**Architecture:** 单个 Python 进程内跑三部分——FastAPI 处理 HTTP/SSE 请求（不执行构建）、APScheduler 后台线程负责到点投递、BuildExecutor 用"调度循环 + 按需工作线程"真正执行构建。三者通过 SQLite 和一个内存队列解耦。前端是无构建步骤的静态页面，用原生 JS + EventSource 消费接口。

**Tech Stack:** Python 3.11 / FastAPI 0.109 / uvicorn 0.52 / SQLAlchemy 2.0 / APScheduler 3.10 / pytest 9.1 / 原生 HTML+JS

**Spec:** `docs/superpowers/specs/2026-09-19-local-ci-tool-design.md`

**落地目录:** `D:\develop\claudecode-workspace\claude_5\CI\`

## Global Constraints

以下约束对**每个任务**都生效，不再逐条重复：

- **零新增 pip 依赖**。只能用：FastAPI、uvicorn、SQLAlchemy、APScheduler、pytest。禁止引入 flask、celery、python-crontab、win10toast、loguru、pydantic-settings 等任何新包。
- **前端零构建**。不使用 npm、不使用任何前端框架、不引入 CDN 资源（工具必须能离线运行）。只用浏览器原生 API。
- **Python 3.11**，目标平台只有 Windows。
- **监听地址固定 `127.0.0.1`，端口固定 `8899`**，不暴露局域网。
- **编码统一 UTF-8**：所有文件读写显式 `encoding="utf-8"`；子进程前置 `chcp 65001`；解码一律 `errors="replace"`。
- **杀子进程一律用 `taskkill /F /T /PID <pid>`**，禁止只用 `proc.kill()`。
- 所有代码注释和界面文案用**中文**。
- 每个任务结束时必须让 `pytest` 全绿才能提交。

## 与 Spec 的一处偏差（已确认）

Spec §7 描述日志通道为"每个 SSE 连接是一个订阅者"（发布订阅模型）。

本计划改为**轮询式 SSE**：SSE 端点在服务端循环调用 `LogHub.snapshot(offset)`，每 200ms 把新增行推给浏览器。

- **对外接口完全不变**：`GET /api/builds/{id}/stream` 仍然是 SSE，事件名仍是 `log` / `status` / `end`。
- **浏览器侧行为完全不变**，仍是实时滚动的控制台。
- **理由**：复用同一套已单元测试覆盖的 offset 逻辑，免掉订阅者注册/注销、慢消费者队列积压、断连泄漏这几类出错点；且 offset 机制天然不会丢行。
- **代价**：最多 200ms 的显示延迟（本地单机使用，不可感知）。

## File Structure

| 文件 | 职责 |
|---|---|
| `CI/pytest.ini` | pytest 配置，把项目根加入 import 路径 |
| `CI/.gitignore` | 忽略运行时产物 |
| `CI/ci_runner/__init__.py` | 包标记，暴露版本号 |
| `CI/ci_runner/config.py` | 路径常量、端口、默认值；支持环境变量覆盖（供测试用） |
| `CI/ci_runner/db.py` | SQLAlchemy 引擎、Session、WAL 设置、建表 |
| `CI/ci_runner/models.py` | 5 张表的 ORM 模型 |
| `CI/ci_runner/loghub.py` | 日志环形缓冲 + 落盘 + offset 快照；文件读取辅助函数 |
| `CI/ci_runner/process.py` | 子进程原语：命令构造、环境变量、进程树清理、带超时的行读取 |
| `CI/ci_runner/executor.py` | 构建编排：投递、并发额度、步骤状态机、超时/中止 |
| `CI/ci_runner/scheduler.py` | APScheduler 封装：cron 注册/同步/校验/预览 |
| `CI/ci_runner/notify.py` | Windows Toast 通知 + 降级提示音 |
| `CI/ci_runner/schemas.py` | Pydantic 请求/响应模型 |
| `CI/ci_runner/api/jobs.py` | 任务 CRUD + 手动触发 + cron 校验 |
| `CI/ci_runner/api/builds.py` | 构建详情 + 日志增量 + SSE + 中止 + 下载 |
| `CI/ci_runner/api/misc.py` | 队列、设置、健康检查 |
| `CI/ci_runner/main.py` | 应用装配、启动/关闭钩子、静态文件托管 |
| `CI/web/index.html` | 单页骨架 |
| `CI/web/style.css` | 全部样式 |
| `CI/web/app.js` | 全部前端逻辑 |
| `CI/tests/conftest.py` | 测试夹具：临时数据目录、干净库、TestClient、Executor |
| `CI/tests/test_models.py` | 模型与建表 |
| `CI/tests/test_loghub.py` | 环形缓冲、offset、落盘 |
| `CI/tests/test_process.py` | 命令构造、编码、进程树清理 |
| `CI/tests/test_executor.py` | 并发、失败即停、超时、中止 |
| `CI/tests/test_api_jobs.py` | 任务 CRUD 校验 |
| `CI/tests/test_api_builds.py` | 构建详情、日志增量、SSE、中止 |
| `CI/tests/test_scheduler.py` | 调度同步、跳过已运行的定时触发 |
| `CI/start.bat` | 双击启动 |
| `CI/README.md` | 使用说明 |

---

## Task 1: 项目骨架、数据库与模型

建立可运行的最小应用：能 import、能建表、`/api/health` 返回 200。

**Files:**
- Create: `CI/pytest.ini`
- Create: `CI/.gitignore`
- Create: `CI/ci_runner/__init__.py`
- Create: `CI/ci_runner/config.py`
- Create: `CI/ci_runner/db.py`
- Create: `CI/ci_runner/models.py`
- Create: `CI/ci_runner/api/__init__.py`
- Create: `CI/ci_runner/api/misc.py`
- Create: `CI/ci_runner/main.py`
- Create: `CI/tests/conftest.py`
- Create: `CI/tests/test_models.py`

**Interfaces:**
- Consumes: 无（起点）
- Produces:
  - `config.DATA_DIR: Path`、`config.LOGS_DIR: Path`、`config.WEB_DIR: Path`、`config.HOST: str`、`config.PORT: int`、`config.APP_VERSION: str`、`config.ensure_dirs() -> None`
  - `db.Base`（DeclarativeBase 子类）、`db.engine`、`db.SessionLocal`、`db.init_db() -> None`、`db.get_session()`（FastAPI 依赖生成器）
  - `models.Job`、`models.Step`、`models.Build`、`models.BuildStep`、`models.Setting`，字段见下方代码
  - `main.app`（FastAPI 实例）

- [ ] **Step 1: 建目录与配置文件**

创建 `CI/pytest.ini`：

```ini
[pytest]
pythonpath = .
testpaths = tests
```

创建 `CI/.gitignore`：

```
__pycache__/
*.pyc
data/
logs/
.pytest_cache/
.venv/
```

创建 `CI/ci_runner/__init__.py`：

```python
"""本地 CI 工具。"""

__version__ = "0.1.0"
```

- [ ] **Step 2: 写配置模块**

创建 `CI/ci_runner/config.py`：

```python
"""全局配置与路径常量。

支持用环境变量覆盖数据目录，测试时据此指向临时目录。
"""

import os
from pathlib import Path

# 项目根目录（ci_runner 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value) if value else default


DATA_DIR = _env_path("CI_DATA_DIR", BASE_DIR / "data")
LOGS_DIR = _env_path("CI_LOGS_DIR", BASE_DIR / "logs")
WEB_DIR = BASE_DIR / "web"
DB_PATH = DATA_DIR / "ci.db"

# 只监听本机，不暴露局域网
HOST = "127.0.0.1"
PORT = 8899

APP_VERSION = "0.1.0"

# 每个构建的日志内存环形缓冲行数
LOG_RING_SIZE = 2000
# 并发额度的默认值与合法区间
DEFAULT_MAX_WORKERS = 4
MIN_MAX_WORKERS = 1
MAX_MAX_WORKERS = 16
# 单步骤超时的默认值与合法区间（秒）
DEFAULT_TIMEOUT_SECONDS = 1800
MIN_TIMEOUT_SECONDS = 60
MAX_TIMEOUT_SECONDS = 86400


def ensure_dirs() -> None:
    """确保运行时目录存在。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def build_log_path(job_id: int, build_number: int) -> Path:
    """构建日志文件路径：logs/<job_id>/<build_number>.log"""
    job_dir = LOGS_DIR / str(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir / f"{build_number}.log"
```

- [ ] **Step 3: 写数据库模块**

创建 `CI/ci_runner/db.py`：

```python
"""SQLAlchemy 引擎、会话与建表。"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from . import config

# Windows 路径要转成 POSIX 风格，SQLAlchemy 的 URL 才能正确解析
DB_URL = f"sqlite:///{config.DB_PATH.as_posix()}"


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


engine = create_engine(
    DB_URL,
    # 构建执行在线程里，连接会被跨线程使用
    connect_args={"check_same_thread": False, "timeout": 30},
    future=True,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """每个连接都开启 WAL 和外键约束。

    WAL 是必须的：调度线程、执行线程、HTTP 线程会并发读写同一个库。
    外键约束默认关闭，不显式打开级联删除不会生效。
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


def init_db() -> None:
    """创建运行时目录并建表。"""
    from . import models  # noqa: F401  导入以注册所有模型

    config.ensure_dirs()
    Base.metadata.create_all(engine)


def get_session():
    """FastAPI 依赖：每个请求一个 Session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: 写 ORM 模型**

创建 `CI/ci_runner/models.py`：

```python
"""ORM 模型：jobs / steps / builds / build_steps / settings。"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Job(Base):
    """一个 CI 任务。"""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="")
    # 步骤执行的基准目录，必须存在且为目录
    workdir: Mapped[str] = mapped_column(String(500), nullable=False)
    # 为空表示不启用定时
    cron_expr: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=1800)
    # True = 步骤失败即停止后续步骤
    fail_fast: Mapped[bool] = mapped_column(Boolean, default=True)
    # False = 定时不触发（手动仍可触发）
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    steps: Mapped[list["Step"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="Step.order_index",
    )
    builds: Mapped[list["Build"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Step(Base):
    """任务里的一个步骤。"""

    __tablename__ = "steps"
    __table_args__ = (UniqueConstraint("job_id", "order_index", name="uq_step_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    command: Mapped[str] = mapped_column(String(4000), nullable=False)
    # "cmd" 或 "powershell"
    shell: Mapped[str] = mapped_column(String(20), default="cmd")
    # 单步骤级别的"失败继续"，优先于 job.fail_fast
    continue_on_failure: Mapped[bool] = mapped_column(Boolean, default=False)
    env: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    job: Mapped["Job"] = relationship(back_populates="steps")


class Build(Base):
    """一次构建。"""

    __tablename__ = "builds"
    __table_args__ = (
        UniqueConstraint("job_id", "build_number", name="uq_build_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    # 每个任务独立自增，从 1 开始
    build_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # queued / running / success / failed / aborted / timeout
    status: Mapped[str] = mapped_column(String(20), default="queued")
    # manual / cron
    trigger: Mapped[str] = mapped_column(String(20), default="manual")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 工具级错误（如工作目录不存在）
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    log_path: Mapped[str] = mapped_column(String(500), default="")

    job: Mapped["Job"] = relationship(back_populates="builds")
    step_results: Mapped[list["BuildStep"]] = relationship(
        back_populates="build",
        cascade="all, delete-orphan",
        order_by="BuildStep.order_index",
    )


class BuildStep(Base):
    """一次构建里某个步骤的执行结果。"""

    __tablename__ = "build_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    build_id: Mapped[int] = mapped_column(
        ForeignKey("builds.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # 冗余存名字：步骤改名后历史记录仍显示当时的名字
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # pending / running / success / failed / skipped / timeout / aborted
    status: Mapped[str] = mapped_column(String(20), default="pending")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    build: Mapped["Build"] = relationship(back_populates="step_results")


class Setting(Base):
    """键值设置表。"""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
```

- [ ] **Step 5: 写健康检查接口**

创建 `CI/ci_runner/api/__init__.py`（空文件）：

```python
```

创建 `CI/ci_runner/api/misc.py`：

```python
"""队列、设置、健康检查接口。"""

from fastapi import APIRouter

from .. import config

router = APIRouter()


@router.get("/health")
def health():
    """给 start.bat 判断服务是否就绪用。"""
    return {
        "status": "ok",
        "version": config.APP_VERSION,
    }
```

- [ ] **Step 6: 写应用装配**

创建 `CI/ci_runner/main.py`：

```python
"""FastAPI 应用装配与启动入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import config
from .api import misc
from .db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="CI Runner", version=config.APP_VERSION, lifespan=lifespan)

app.include_router(misc.router, prefix="/api", tags=["misc"])
```

- [ ] **Step 7: 写测试夹具**

创建 `CI/tests/conftest.py`：

```python
"""测试夹具。

关键点：必须在 import ci_runner 之前设置环境变量，
因为 config 模块在 import 时就会算出 DATA_DIR / LOGS_DIR。
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# 指向临时目录，绝不碰真实的 data/ 和 logs/
_TMP_ROOT = Path(tempfile.mkdtemp(prefix="ci-runner-test-"))
os.environ["CI_DATA_DIR"] = str(_TMP_ROOT / "data")
os.environ["CI_LOGS_DIR"] = str(_TMP_ROOT / "logs")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from ci_runner.db import Base, SessionLocal, engine  # noqa: E402
from ci_runner.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_tmp_root():
    yield
    shutil.rmtree(_TMP_ROOT, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_db():
    """每个测试一张全新的空表。"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
```

- [ ] **Step 8: 写第一个测试**

创建 `CI/tests/test_models.py`：

```python
"""模型与建表。"""

from ci_runner.models import Build, BuildStep, Job, Setting, Step


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_tables_created(engine_tables):
    assert {
        "jobs",
        "steps",
        "builds",
        "build_steps",
        "settings",
    } <= engine_tables


def test_job_with_steps_cascade_delete(session):
    job = Job(name="demo", workdir=".", fail_fast=True)
    job.steps = [
        Step(order_index=0, name="第一步", command="echo a"),
        Step(order_index=1, name="第二步", command="echo b"),
    ]
    session.add(job)
    session.commit()
    job_id = job.id

    session.delete(job)
    session.commit()

    assert session.query(Step).filter_by(job_id=job_id).count() == 0


def test_delete_job_cascades_builds(session):
    job = Job(name="demo2", workdir=".")
    session.add(job)
    session.commit()

    build = Build(job_id=job.id, build_number=1, status="success")
    build.step_results = [
        BuildStep(step_id=1, name="第一步", order_index=0, status="success"),
    ]
    session.add(build)
    session.commit()
    build_id = build.id

    session.delete(job)
    session.commit()

    assert session.query(Build).filter_by(id=build_id).count() == 0
    assert session.query(BuildStep).filter_by(build_id=build_id).count() == 0


def test_setting_roundtrip(session):
    session.add(Setting(key="max_workers", value="4"))
    session.commit()

    got = session.get(Setting, "max_workers")
    assert got.value == "4"
```

在 `CI/tests/conftest.py` 末尾追加 `engine_tables` 夹具：

```python
@pytest.fixture
def engine_tables():
    """当前库里的所有表名。"""
    from sqlalchemy import inspect

    return set(inspect(engine).get_table_names())
```

- [ ] **Step 9: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

预期：5 个测试全部 PASS。

- [ ] **Step 10: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/pytest.ini CI/.gitignore CI/ci_runner CI/tests && git commit -m "feat(ci): 项目骨架、数据库模型与健康检查接口"
```

---

## Task 2: LogHub 日志中心

构建日志的单一入口：环形缓冲 + 落盘 + offset 快照。这是 SSE 和控制台页面的数据源。

**Files:**
- Create: `CI/ci_runner/loghub.py`
- Create: `CI/tests/test_loghub.py`

**Interfaces:**
- Consumes: `config.LOG_RING_SIZE`
- Produces:
  - `LogHub(log_path: Path, ring_size: int = 2000)`
    - `.write(line: str) -> None`
    - `.snapshot(offset: int = 0) -> dict` → `{"lines": list[str], "next_offset": int, "truncated": bool}`
    - `.total() -> int`
  - `read_log_file(path: Path, offset: int = 0) -> dict`（同样的返回结构）

**设计要点：** `next_offset` 是"累计写入行数"，不因环形缓冲丢弃而回退。客户端拿它当下次请求的 `offset`。

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_loghub.py`：

```python
"""日志环形缓冲与 offset 快照。"""

from pathlib import Path

from ci_runner.loghub import LogHub, read_log_file


def test_write_and_snapshot_from_zero(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    hub.write("第一行")
    hub.write("第二行")

    snap = hub.snapshot(0)
    assert snap["lines"] == ["第一行", "第二行"]
    assert snap["next_offset"] == 2
    assert snap["truncated"] is False


def test_snapshot_incremental(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    hub.write("a")
    hub.write("b")

    first = hub.snapshot(0)
    hub.write("c")
    second = hub.snapshot(first["next_offset"])

    assert second["lines"] == ["c"]
    assert second["next_offset"] == 3


def test_ring_drops_oldest_but_offset_keeps_growing(tmp_path):
    hub = LogHub(tmp_path / "1.log", ring_size=3)
    for i in range(10):
        hub.write(f"line-{i}")

    snap = hub.snapshot(0)
    assert snap["lines"] == ["line-7", "line-8", "line-9"]
    assert snap["next_offset"] == 10
    # 客户端要的 offset 已经掉出窗口，必须告诉它被截断了
    assert snap["truncated"] is True


def test_snapshot_at_ring_window_boundary_is_not_truncated(tmp_path):
    hub = LogHub(tmp_path / "1.log", ring_size=3)
    for i in range(10):
        hub.write(f"line-{i}")

    snap = hub.snapshot(7)
    assert snap["lines"] == ["line-7", "line-8", "line-9"]
    assert snap["truncated"] is False


def test_log_file_content_matches_all_lines(tmp_path):
    path = tmp_path / "1.log"
    hub = LogHub(path, ring_size=3)
    for i in range(10):
        hub.write(f"line-{i}")

    # 环形缓冲只留 3 行，但文件必须留全部 10 行
    content = path.read_text(encoding="utf-8").splitlines()
    assert content == [f"line-{i}" for i in range(10)]


def test_chinese_lines_survive_roundtrip(tmp_path):
    path = tmp_path / "1.log"
    hub = LogHub(path)
    hub.write("构建失败：找不到模块 pytest")

    assert hub.snapshot(0)["lines"] == ["构建失败：找不到模块 pytest"]
    assert "构建失败：找不到模块 pytest" in path.read_text(encoding="utf-8")


def test_read_log_file_missing_returns_empty(tmp_path):
    result = read_log_file(tmp_path / "nope.log")
    assert result == {"lines": [], "next_offset": 0, "truncated": False}


def test_read_log_file_with_offset(tmp_path):
    path = tmp_path / "1.log"
    path.write_text("a\nb\nc\n", encoding="utf-8")

    result = read_log_file(path, offset=1)
    assert result["lines"] == ["b", "c"]
    assert result["next_offset"] == 3


def test_write_is_thread_safe(tmp_path):
    """并发写入不能丢行。"""
    import threading

    hub = LogHub(tmp_path / "1.log", ring_size=100000)

    def worker(tag):
        for i in range(200):
            hub.write(f"{tag}-{i}")

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert hub.total() == 800
    assert len(read_log_file(tmp_path / "1.log")["lines"]) == 800
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_loghub.py -v
```

预期：全部 FAIL，报 `ModuleNotFoundError: No module named 'ci_runner.loghub'`。

- [ ] **Step 3: 实现 LogHub**

创建 `CI/ci_runner/loghub.py`：

```python
"""构建日志中心：环形缓冲 + 落盘 + offset 快照。

offset 的语义是"累计写入行数"（从 0 开始的下一行编号），
不随环形缓冲丢弃旧行而回退。客户端拿 next_offset 当下次请求的 offset。
"""

import threading
from collections import deque
from pathlib import Path

from . import config


class LogHub:
    """一次构建的日志。写入方是执行线程，读取方是 HTTP 线程。"""

    def __init__(self, log_path: Path, ring_size: int | None = None):
        self._log_path = Path(log_path)
        self._ring: deque[str] = deque(
            maxlen=ring_size if ring_size is not None else config.LOG_RING_SIZE
        )
        self._lock = threading.Lock()
        # 累计写入行数，只增不减
        self._total = 0

    def write(self, line: str) -> None:
        """写一行：进环形缓冲 + 追加到文件。

        锁只保护内存状态，文件写入放在锁外，避免慢磁盘拖住其他线程。
        """
        with self._lock:
            self._ring.append(line)
            self._total += 1

        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def total(self) -> int:
        """累计写入行数。"""
        with self._lock:
            return self._total

    def snapshot(self, offset: int = 0) -> dict:
        """取 offset 之后的行。

        offset 若已掉出环形窗口，返回窗口内的全部行并置 truncated=True。
        """
        with self._lock:
            total = self._total
            ring = list(self._ring)

        window_start = total - len(ring)
        if offset < window_start:
            start = window_start
            truncated = True
        else:
            start = offset
            truncated = False

        lines = ring[start - window_start :]
        return {
            "lines": lines,
            "next_offset": total,
            "truncated": truncated,
        }


def read_log_file(path: Path, offset: int = 0) -> dict:
    """从日志文件读 offset 之后的行。

    用于查看已经结束、内存缓冲已释放的历史构建。
    """
    path = Path(path)
    if not path.exists():
        return {"lines": [], "next_offset": 0, "truncated": False}

    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    return {
        "lines": lines[offset:],
        "next_offset": len(lines),
        "truncated": False,
    }
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_loghub.py -v
```

预期：9 个测试全部 PASS。

- [ ] **Step 5: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner/loghub.py CI/tests/test_loghub.py && git commit -m "feat(ci): 日志中心 LogHub（环形缓冲 + offset 快照）"
```

---

## Task 3: 子进程执行原语

把"怎么在 Windows 上正确跑一条命令并拿到输出"独立出来，这是整个工具最容易出问题的部分。

**Files:**
- Create: `CI/ci_runner/process.py`
- Create: `CI/tests/test_process.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `build_command(shell: str, command: str) -> list[str]`
  - `build_env(extra: dict | None) -> dict[str, str]`
  - `kill_process_tree(pid: int) -> None`
  - `RunResult` dataclass：`exit_code: int | None`、`timed_out: bool`、`aborted: bool`
  - `run_command(command, shell, workdir, env, timeout, log_path, abort_event=None) -> RunResult`

`run_command` 的日志写入直接走 `LogHub`（由调用方创建并传入 `log_path`），这样这个模块不需要知道构建的概念，只负责"跑命令 + 记日志"。

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_process.py`：

```python
"""子进程原语：命令构造、环境、进程树清理、超时、中止。"""

import threading
import time
from pathlib import Path

from ci_runner.loghub import LogHub, read_log_file
from ci_runner.process import build_command, build_env, kill_process_tree, run_command


def test_build_command_cmd_switches_codepage():
    cmd = build_command("cmd", "npm run build")
    assert cmd[0].lower().endswith("cmd.exe")
    assert cmd[1] == "/c"
    # 必须切到 UTF-8 代码页，否则中文输出乱码
    assert "chcp 65001" in cmd[2]
    assert "npm run build" in cmd[2]


def test_build_command_powershell():
    cmd = build_command("powershell", "Write-Host 你好")
    assert cmd[0].lower().endswith("powershell.exe")
    assert "-NoProfile" in cmd
    assert "-Command" in cmd


def test_build_env_forces_utf8():
    env = build_env(None)
    assert env["PYTHONIOENCODING"] == "utf-8"
    assert env["PYTHONUTF8"] == "1"


def test_build_env_merges_extra():
    env = build_env({"MY_FLAG": "1", "NUM": 42})
    assert env["MY_FLAG"] == "1"
    # 非字符串值必须被转成字符串，否则 Popen 会报错
    assert env["NUM"] == "42"


def test_run_command_success(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    result = run_command(
        command="echo hello",
        shell="cmd",
        workdir=str(tmp_path),
        env=None,
        timeout=30,
        hub=hub,
    )
    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.aborted is False
    assert "hello" in "\n".join(hub.snapshot(0)["lines"])


def test_run_command_preserves_chinese_output(tmp_path):
    """中文输出不能变成乱码或问号。"""
    hub = LogHub(tmp_path / "1.log")
    run_command(
        command="echo 构建成功中文测试",
        shell="cmd",
        workdir=str(tmp_path),
        env=None,
        timeout=30,
        hub=hub,
    )
    text = "\n".join(hub.snapshot(0)["lines"])
    assert "构建成功中文测试" in text


def test_run_command_reports_nonzero_exit(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    result = run_command(
        command="exit 3",
        shell="cmd",
        workdir=str(tmp_path),
        env=None,
        timeout=30,
        hub=hub,
    )
    assert result.exit_code == 3


def test_run_command_timeout_kills_process_tree(tmp_path):
    """超时必须连子孙进程一起杀掉，不能只杀父进程。"""
    hub = LogHub(tmp_path / "1.log")
    marker = tmp_path / "child-still-alive.txt"
    # 父进程启动一个每秒写文件的子进程，然后自己长时间睡眠
    script = (
        f'start /b cmd /c "for /l %i in (1,1,30) do '
        f'(echo alive>>"{marker}" & timeout /t 1 >nul)" & timeout /t 30 >nul'
    )
    started = time.monotonic()
    result = run_command(
        command=script,
        shell="cmd",
        workdir=str(tmp_path),
        env=None,
        timeout=2,
        hub=hub,
    )
    assert result.timed_out is True
    assert time.monotonic() - started < 15

    # 等一会儿，确认那个写文件的子进程确实也没了
    time.sleep(2)
    size_before = marker.stat().st_size if marker.exists() else 0
    time.sleep(3)
    size_after = marker.stat().st_size if marker.exists() else 0
    assert size_after == size_before, "子进程还在写文件，说明进程树没被清理"


def test_run_command_abort(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    abort = threading.Event()

    def trigger():
        time.sleep(1)
        abort.set()

    threading.Thread(target=trigger, daemon=True).start()
    started = time.monotonic()
    result = run_command(
        command="timeout /t 30 >nul",
        shell="cmd",
        workdir=str(tmp_path),
        env=None,
        timeout=60,
        hub=hub,
        abort_event=abort,
    )
    assert result.aborted is True
    assert time.monotonic() - started < 10


def test_run_command_missing_workdir_returns_error(tmp_path):
    hub = LogHub(tmp_path / "1.log")
    result = run_command(
        command="echo hi",
        shell="cmd",
        workdir=str(tmp_path / "does-not-exist"),
        env=None,
        timeout=10,
        hub=hub,
    )
    assert result.exit_code is None
    assert result.error is not None
    assert "工作目录" in result.error


def test_kill_process_tree_ignores_dead_pid(capsys):
    """杀一个不存在的进程不能抛异常。"""
    kill_process_tree(999999)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_process.py -v
```

预期：全部 FAIL，报 `ModuleNotFoundError: No module named 'ci_runner.process'`。

- [ ] **Step 3: 实现 process.py**

创建 `CI/ci_runner/process.py`：

```python
"""Windows 子进程执行原语。

这个模块只做一件事：在 Windows 上正确地跑一条命令、拿到它的输出、
并在超时或中止时把整棵进程树清理干净。
"""

import os
import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field

from .loghub import LogHub

# 让子进程独立成组，避免工具的 Ctrl+C 传染过去
CREATE_NEW_PROCESS_GROUP = 0x00000200
# 不弹出控制台窗口
CREATE_NO_WINDOW = 0x08000000

# 读取输出的轮询间隔
_POLL_INTERVAL = 0.2


@dataclass
class RunResult:
    """一条命令的执行结果。"""

    exit_code: int | None = None
    timed_out: bool = False
    aborted: bool = False
    # 工具级错误（如工作目录不存在），区别于命令自己的非零退出码
    error: str | None = None


def build_command(shell: str, command: str) -> list[str]:
    """把步骤配置转成 Popen 的参数列表。

    cmd 分支前置 chcp 65001：中文 Windows 默认代码页是 GBK，
    不切换的话子进程输出的中文会变成乱码。
    """
    if shell == "powershell":
        return [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ]
    return ["cmd.exe", "/c", f"chcp 65001 > nul && {command}"]


def build_env(extra: dict | None) -> dict[str, str]:
    """构造子进程环境变量。"""
    env = os.environ.copy()
    # Python 子进程默认用 GBK 输出，强制成 UTF-8
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    if extra:
        # 值必须是字符串，否则 Popen 会报 TypeError
        env.update({str(k): str(v) for k, v in extra.items()})
    return env


def kill_process_tree(pid: int) -> None:
    """杀掉整棵进程树。

    npm run build 会派生 node 子进程，只调 proc.kill() 杀不掉孙子进程，
    会留下僵尸进程占着 CPU 和文件锁。/T 就是"连子孙一起杀"。
    """
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
            timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        # 进程可能已经自己退出了，杀掉不存在的东西不算错误
        pass


def _pump_output(proc: subprocess.Popen, sink: queue.Queue) -> None:
    """把子进程输出逐行塞进队列，读完放一个 None 表示结束。"""
    try:
        for line in proc.stdout:
            sink.put(line.rstrip("\r\n"))
    except (ValueError, OSError):
        # 管道被强制关闭时会走到这里，属于中止/超时的正常路径
        pass
    finally:
        sink.put(None)


def run_command(
    command: str,
    shell: str,
    workdir: str,
    env: dict | None,
    timeout: int,
    hub: LogHub,
    abort_event: threading.Event | None = None,
) -> RunResult:
    """跑一条命令，把输出实时写进 hub。"""
    if not os.path.isdir(workdir):
        msg = f"工作目录不存在或不是目录：{workdir}"
        hub.write(f"[error] {msg}")
        return RunResult(error=msg)

    try:
        proc = subprocess.Popen(
            build_command(shell, command),
            cwd=workdir,
            env=build_env(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            # 宁可个别字符变问号，也绝不能因为解码异常打断构建
            errors="replace",
            bufsize=1,
            creationflags=CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
        )
    except OSError as exc:
        msg = f"启动命令失败：{exc}"
        hub.write(f"[error] {msg}")
        return RunResult(error=msg)

    sink: queue.Queue = queue.Queue()
    reader = threading.Thread(target=_pump_output, args=(proc, sink), daemon=True)
    reader.start()

    deadline = time.monotonic() + timeout
    result = RunResult()

    while True:
        if abort_event is not None and abort_event.is_set():
            result.aborted = True
            kill_process_tree(proc.pid)
            break

        if time.monotonic() > deadline:
            result.timed_out = True
            kill_process_tree(proc.pid)
            break

        try:
            line = sink.get(timeout=_POLL_INTERVAL)
        except queue.Empty:
            continue

        if line is None:
            # 输出流结束，命令自己跑完了
            break

        hub.write(line)

    # 把管道里剩下的行排空，避免丢失最后几行
    while True:
        try:
            line = sink.get_nowait()
        except queue.Empty:
            break
        if line is not None:
            hub.write(line)

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        kill_process_tree(proc.pid)
        proc.wait(timeout=10)

    result.exit_code = proc.returncode
    return result
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_process.py -v
```

预期：12 个测试全部 PASS。

注意 `test_run_command_timeout_kills_process_tree` 会实际等约 7 秒，属正常。

- [ ] **Step 5: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner/process.py CI/tests/test_process.py && git commit -m "feat(ci): Windows 子进程执行原语（UTF-8/进程树清理/超时中止）"
```

---

## Task 4: 构建编排与并发调度

整个工具最核心的部分：投递、并发额度、步骤状态机、失败策略、超时、中止。

**Files:**
- Create: `CI/ci_runner/executor.py`
- Create: `CI/tests/test_executor.py`

**Interfaces:**
- Consumes: `config`、`db.SessionLocal`、`loghub.LogHub`、`loghub.read_log_file`、`process.run_command`
- Produces:
  - 异常：`JobBusyError`（该任务已有构建在排队）
  - `Executor(session_factory=SessionLocal)`
    - `.start() -> None` / `.shutdown() -> None`
    - `.trigger(job_id: int, trigger: str = "manual") -> int`（返回 build_id；忙碌时抛 `JobBusyError`）
    - `.abort(build_id: int) -> None`
    - `.get_hub(build_id: int) -> LogHub | None`
    - `.running_count() -> int` / `.queued_ids() -> list[int]`
    - `.wait_idle(timeout: float = 30.0) -> bool`（测试用）
  - 设置键 `max_workers`（存 `settings` 表）

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_executor.py`：

```python
"""构建编排：并发、失败即停、超时、中止。"""

import time

import pytest

from ci_runner.db import SessionLocal
from ci_runner.executor import Executor, JobBusyError
from ci_runner.models import Build, BuildStep, Job, Step


def make_job(session, name, commands, workdir, **kwargs):
    """commands 是 (命令, 是否失败继续) 的列表。"""
    job = Job(name=name, workdir=str(workdir), **kwargs)
    job.steps = [
        Step(
            order_index=i,
            name=f"步骤{i}",
            command=cmd,
            shell="cmd",
            continue_on_failure=cont,
        )
        for i, (cmd, cont) in enumerate(commands)
    ]
    session.add(job)
    session.commit()
    return job.id


@pytest.fixture
def executor():
    ex = Executor(session_factory=SessionLocal)
    ex.start()
    yield ex
    ex.shutdown()


def wait_for_status(session, build_id, timeout=30):
    """轮询直到构建结束。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        session.expire_all()
        build = session.get(Build, build_id)
        if build.status not in ("queued", "running"):
            return build
        time.sleep(0.1)
    raise AssertionError(f"构建 {build_id} 在 {timeout} 秒内没有结束")


def test_successful_build(executor, session, tmp_path):
    job_id = make_job(session, "ok", [("echo hello", False)], tmp_path)
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)
    assert build.status == "success"
    assert build.exit_code == 0
    assert build.started_at is not None
    assert build.finished_at is not None


def test_fail_fast_skips_remaining_steps(executor, session, tmp_path):
    job_id = make_job(
        session,
        "failfast",
        [("echo first", False), ("exit 1", False), ("echo never", False)],
        tmp_path,
        fail_fast=True,
    )
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)

    assert build.status == "failed"
    statuses = [s.status for s in build.step_results]
    assert statuses == ["success", "failed", "skipped"]


def test_continue_on_failure_runs_remaining_steps(executor, session, tmp_path):
    job_id = make_job(
        session,
        "continue",
        [("exit 1", True), ("echo still-runs", False)],
        tmp_path,
        fail_fast=True,
    )
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)

    # 整体仍然是失败的，但后续步骤确实执行了
    assert build.status == "failed"
    assert [s.status for s in build.step_results] == ["failed", "success"]


def test_job_fail_fast_false_continues_all_steps(executor, session, tmp_path):
    job_id = make_job(
        session,
        "nofailfast",
        [("exit 1", False), ("echo second", False)],
        tmp_path,
        fail_fast=False,
    )
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)

    assert build.status == "failed"
    assert [s.status for s in build.step_results] == ["failed", "success"]


def test_same_job_allows_one_queued_then_rejects(executor, session, tmp_path):
    """正在跑时再触发 → 排队；已有 1 个在排队时再触发 → 拒绝。"""
    job_id = make_job(session, "busy", [("timeout /t 3 >nul", False)], tmp_path)

    # 第一次：进队列并开跑
    first = executor.trigger(job_id)

    # 第二次：正在跑，允许排 1 个
    second = executor.trigger(job_id)
    assert second != first

    # 第三次：已经有 1 个在排队了，拒绝
    with pytest.raises(JobBusyError):
        executor.trigger(job_id)


def test_different_jobs_run_in_parallel(executor, session, tmp_path):
    a = make_job(session, "par-a", [("timeout /t 2 >nul", False)], tmp_path)
    b = make_job(session, "par-b", [("timeout /t 2 >nul", False)], tmp_path)

    a_id = executor.trigger(a)
    b_id = executor.trigger(b)

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        session.expire_all()
        if (
            session.get(Build, a_id).status == "running"
            and session.get(Build, b_id).status == "running"
        ):
            break
        time.sleep(0.05)
    else:
        raise AssertionError("两个任务没有同时进入 running，并发没生效")


def test_max_workers_limits_concurrency(executor, session, tmp_path):
    from ci_runner.settings_store import set_setting

    set_setting(session, "max_workers", "1")
    session.commit()

    ids = [
        executor.trigger(make_job(session, f"limit-{i}", [("timeout /t 1 >nul", False)], tmp_path))
        for i in range(3)
    ]

    time.sleep(1.5)
    session.expire_all()
    statuses = [session.get(Build, i).status for i in ids]
    # 额度是 1，任意时刻最多一个在跑
    assert statuses.count("running") <= 1

    executor.wait_idle(timeout=30)
    session.expire_all()
    assert all(session.get(Build, i).status == "success" for i in ids)


def test_step_timeout_marks_build_timeout(executor, session, tmp_path):
    job_id = make_job(session, "slow", [("timeout /t 30 >nul", False)], tmp_path)
    session.get(Job, job_id).timeout_seconds = 2
    session.commit()

    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id, timeout=30)

    assert build.status == "timeout"
    assert build.step_results[0].status == "timeout"


def test_abort_running_build(executor, session, tmp_path):
    job_id = make_job(session, "abortme", [("timeout /t 30 >nul", False)], tmp_path)
    build_id = executor.trigger(job_id)

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        session.expire_all()
        if session.get(Build, build_id).status == "running":
            break
        time.sleep(0.05)

    executor.abort(build_id)
    build = wait_for_status(session, build_id)
    assert build.status == "aborted"
    assert build.step_results[0].status == "aborted"


def test_abort_queued_build_never_starts(executor, session, tmp_path):
    """排队中的构建被中止后，不应该启动任何子进程。"""
    from ci_runner.settings_store import set_setting

    set_setting(session, "max_workers", "1")
    session.commit()

    blocker = executor.trigger(
        make_job(session, "blocker", [("timeout /t 3 >nul", False)], tmp_path)
    )
    job_id = make_job(session, "queued", [("echo should-not-run", False)], tmp_path)
    queued_build = executor.trigger(job_id)

    executor.abort(queued_build)
    session.expire_all()
    assert session.get(Build, queued_build).status == "aborted"

    executor.wait_idle(timeout=30)
    session.expire_all()
    # 被中止的构建从未产生步骤结果（步骤结果在真正开跑时才初始化）
    build = session.get(Build, queued_build)
    assert build.started_at is None
    assert build.step_results == []


def test_build_number_increments_per_job(executor, session, tmp_path):
    job_id = make_job(session, "numbered", [("echo hi", False)], tmp_path)

    first = executor.trigger(job_id)
    wait_for_status(session, first)
    second = executor.trigger(job_id)
    wait_for_status(session, second)

    assert session.get(Build, first).build_number == 1
    assert session.get(Build, second).build_number == 2


def test_log_file_is_written(executor, session, tmp_path):
    job_id = make_job(session, "logfile", [("echo 日志内容测试", False)], tmp_path)
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)

    from pathlib import Path

    content = Path(build.log_path).read_text(encoding="utf-8")
    assert "日志内容测试" in content


def test_missing_workdir_fails_build(executor, session, tmp_path):
    job_id = make_job(session, "badworkdir", [("echo hi", False)], tmp_path / "nope")
    build_id = executor.trigger(job_id)
    build = wait_for_status(session, build_id)

    assert build.status == "failed"
    assert build.error_message is not None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_executor.py -v
```

预期：全部 FAIL，报 `ModuleNotFoundError: No module named 'ci_runner.executor'`。

- [ ] **Step 3: 写设置读写小模块**

创建 `CI/ci_runner/settings_store.py`：

```python
"""settings 表的读写封装。

故意做成独立小模块：executor、api 都要用，放在任何一边都会造成循环依赖。
"""

from sqlalchemy.orm import Session

from . import config
from .models import Setting

_ALLOWED = {
    "max_workers": (str(config.MIN_MAX_WORKERS), str(config.MAX_MAX_WORKERS)),
    "notify_on_success_manual": ("0", "1"),
    "notify_on_success_cron": ("0", "1"),
    "notify_on_failure": ("0", "1"),
}

DEFAULTS = {
    "max_workers": str(config.DEFAULT_MAX_WORKERS),
    "notify_on_success_manual": "1",
    "notify_on_success_cron": "0",
    "notify_on_failure": "1",
}


def get_setting(db: Session, key: str) -> str:
    """读设置，没有就返回默认值。"""
    row = db.get(Setting, key)
    if row is not None:
        return row.value
    return DEFAULTS.get(key, "")


def set_setting(db: Session, key: str, value: str) -> None:
    """写设置。key 不存在则新建。"""
    row = db.get(Setting, key)
    if row is None:
        db.add(Setting(key=key, value=str(value)))
    else:
        row.value = str(value)


def get_int_setting(db: Session, key: str) -> int:
    try:
        return int(get_setting(db, key))
    except (TypeError, ValueError):
        return int(DEFAULTS.get(key, "0"))


def get_bool_setting(db: Session, key: str) -> bool:
    return get_setting(db, key) == "1"


def all_settings(db: Session) -> dict:
    """界面上要展示的全部设置。"""
    return {key: get_setting(db, key) for key in DEFAULTS}
```

- [ ] **Step 4: 实现 executor.py**

创建 `CI/ci_runner/executor.py`：

```python
"""构建编排：投递、并发额度、步骤状态机。

线程模型：
- 一个调度循环线程，按 max_workers 决定何时派发队列里的构建
- 每个正在跑的构建占一个工作线程
- 工作线程内部用 process.run_command 顺序执行步骤
"""

import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from . import config
from .db import SessionLocal
from .loghub import LogHub, read_log_file
from .models import Build, BuildStep, Job
from .process import run_command
from .settings_store import get_int_setting

# 调度循环的唤醒间隔
_DISPATCH_INTERVAL = 0.5


class JobBusyError(RuntimeError):
    """该任务已有构建在排队。"""


@dataclass(frozen=True)
class _StepSpec:
    """步骤的纯数据快照。

    Session 关闭后 ORM 对象的属性访问是惰性加载，跨会话读取很脆弱。
    开跑前一次性拷成不可变数据，工作线程后面就再也不碰 Session 里的 ORM 对象。
    """

    id: int
    name: str
    command: str
    shell: str
    continue_on_failure: bool
    env: dict | None


# 保证同一任务的 build_number 不重号。
# SQLite 不支持 SELECT ... FOR UPDATE，但本工具是单进程，
# 进程内的每任务锁就足以串行化分配；DB 上还有唯一约束兜底。
_number_locks: dict[int, threading.Lock] = {}
_number_locks_guard = threading.Lock()


def _number_lock(job_id: int) -> threading.Lock:
    with _number_locks_guard:
        lock = _number_locks.get(job_id)
        if lock is None:
            lock = threading.Lock()
            _number_locks[job_id] = lock
        return lock


def _now() -> datetime:
    return datetime.now()


class Executor:
    """构建执行器。"""

    def __init__(self, session_factory: sessionmaker = SessionLocal):
        self._session_factory = session_factory
        self._hubs: dict[int, LogHub] = {}
        # 中止信号，每个正在跑的构建一个
        self._abort_events: dict[int, threading.Event] = {}
        self._running: set[int] = set()
        self._queue: list[int] = []
        self._lock = threading.Lock()
        self._wakeup = threading.Event()
        self._stop = threading.Event()
        self._dispatcher: threading.Thread | None = None

    # ---------- 生命周期 ----------

    def start(self) -> None:
        # 幂等：重复调用不能起第二个调度循环
        # （main.py 的 lifespan 会在测试已注入 executor 后再调一次 start）
        with self._lock:
            if self._dispatcher is not None and self._dispatcher.is_alive():
                return
        self._stop.clear()
        self._resume_pending()
        self._dispatcher = threading.Thread(
            target=self._dispatch_loop, name="ci-dispatcher", daemon=True
        )
        self._dispatcher.start()

    def shutdown(self) -> None:
        """停止调度并中止所有在跑的构建。"""
        self._stop.set()
        self._wakeup.set()
        if self._dispatcher is not None:
            self._dispatcher.join(timeout=5)

        with self._lock:
            running = list(self._running)
        for build_id in running:
            self.abort(build_id)

        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            with self._lock:
                if not self._running:
                    break
            time.sleep(0.1)

    def _resume_pending(self) -> None:
        """启动时把上次进程退出时残留的 queued 构建重新排队。

        进程被强杀时可能有构建停在 queued，不清理会永远卡住。
        """
        with self._session_factory() as db:
            stale = db.query(Build).filter_by(status="queued").all()
            for build in stale:
                build.status = "aborted"
                build.error_message = "工具重启，构建未执行"
                build.finished_at = _now()
            db.commit()

    # ---------- 查询 ----------

    def get_hub(self, build_id: int) -> LogHub | None:
        with self._lock:
            return self._hubs.get(build_id)

    def running_count(self) -> int:
        with self._lock:
            return len(self._running)

    def queued_ids(self) -> list[int]:
        with self._lock:
            return list(self._queue)

    def wait_idle(self, timeout: float = 30.0) -> bool:
        """等所有构建结束。测试用。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                idle = not self._running and not self._queue
            if idle:
                return True
            time.sleep(0.1)
        return False

    # ---------- 投递 ----------

    def trigger(self, job_id: int, trigger: str = "manual") -> int:
        """投递一次构建，返回 build_id。"""
        with self._session_factory() as db:
            job = db.get(Job, job_id)
            if job is None:
                raise ValueError(f"任务不存在：{job_id}")

            # 同一任务最多一个排队中的构建，避免误点十下堆出十个
            pending = (
                db.query(Build)
                .filter(Build.job_id == job_id, Build.status == "queued")
                .first()
            )
            if pending is not None:
                raise JobBusyError("该任务已有构建在排队")

            with _number_lock(job_id):
                last = (
                    db.query(Build)
                    .filter_by(job_id=job_id)
                    .order_by(Build.build_number.desc())
                    .first()
                )
                build_number = (last.build_number + 1) if last else 1

                log_path = config.build_log_path(job_id, build_number)
                build = Build(
                    job_id=job_id,
                    build_number=build_number,
                    status="queued",
                    trigger=trigger,
                    log_path=str(log_path),
                )
                db.add(build)
                db.commit()
                build_id = build.id

        # 日志文件开头写构建元信息，方便脱离界面直接看文件
        with self._session_factory() as db:
            job = db.get(Job, job_id)
            hub = LogHub(Path(build.log_path))
            hub.write(f"任务：{job.name}")
            hub.write(f"构建号：#{build_number}  触发方式：{trigger}")
            hub.write(f"工作目录：{job.workdir}")
            hub.write(f"开始时间：{_now():%Y-%m-%d %H:%M:%S}")
            hub.write("=" * 60)
            with self._lock:
                self._hubs[build_id] = hub
                self._abort_events[build_id] = threading.Event()
                self._queue.append(build_id)

        # 立刻唤醒调度循环，不用等下一次轮询
        self._wakeup.set()
        return build_id

    def abort(self, build_id: int) -> None:
        """中止构建。queued 的直接出队，running 的由工作线程杀进程树。"""
        with self._lock:
            if build_id in self._queue:
                self._queue.remove(build_id)
                event = self._abort_events.get(build_id)
                queued_only = True
            else:
                event = self._abort_events.get(build_id)
                queued_only = False

        if event is not None:
            event.set()

        if queued_only:
            with self._session_factory() as db:
                build = db.get(Build, build_id)
                if build is not None and build.status == "queued":
                    build.status = "aborted"
                    build.error_message = "排队中被中止"
                    build.finished_at = _now()
                    db.commit()

    # ---------- 调度 ----------

    def _dispatch_loop(self) -> None:
        while not self._stop.is_set():
            build_id = self._pick_next()
            if build_id is None:
                self._wakeup.wait(_DISPATCH_INTERVAL)
                self._wakeup.clear()
                continue

            threading.Thread(
                target=self._run_build,
                args=(build_id,),
                name=f"ci-build-{build_id}",
                daemon=True,
            ).start()

    def _pick_next(self) -> int | None:
        """有额度且队列非空就取一个。额度每次从设置表读，改完立即生效。"""
        with self._session_factory() as db:
            limit = get_int_setting(db, "max_workers")

        with self._lock:
            if self._queue and len(self._running) < limit:
                build_id = self._queue.pop(0)
                self._running.add(build_id)
                return build_id
        return None

    # ---------- 执行 ----------

    def _run_build(self, build_id: int) -> None:
        try:
            self._execute(build_id)
        except Exception as exc:  # noqa: BLE001  工作线程绝不能把异常抛出去
            with self._session_factory() as db:
                build = db.get(Build, build_id)
                if build is not None:
                    build.status = "failed"
                    build.error_message = f"执行器内部错误：{exc}"
                    build.finished_at = _now()
                    db.commit()
        finally:
            with self._lock:
                self._running.discard(build_id)
            self._wakeup.set()

    def _execute(self, build_id: int) -> None:
        # 在一个会话里把要用的数据全部拷出来，之后工作线程不再依赖 Session
        with self._session_factory() as db:
            build = db.get(Build, build_id)
            job = db.get(Job, build.job_id)
            workdir: str = job.workdir
            timeout_seconds: int = job.timeout_seconds
            fail_fast: bool = job.fail_fast
            steps: list[_StepSpec] = [
                _StepSpec(
                    id=s.id,
                    name=s.name,
                    command=s.command,
                    shell=s.shell,
                    continue_on_failure=s.continue_on_failure,
                    env=s.env,
                )
                for s in job.steps
            ]

        abort_event = self._abort_events.get(build_id) or threading.Event()
        hub = self._hubs.get(build_id)
        if hub is None:
            return

        # 真正开跑才写 started_at
        with self._session_factory() as db:
            build = db.get(Build, build_id)
            build.status = "running"
            build.started_at = _now()
            db.commit()

        # 工作目录不存在属于工具级错误，直接在开跑前拦下
        if not os.path.isdir(workdir):
            msg = f"工作目录不存在或不是目录：{workdir}"
            hub.write(f"[error] {msg}")
            hub.write("构建终止。")
            with self._session_factory() as db:
                build = db.get(Build, build_id)
                build.status = "failed"
                build.error_message = msg
                build.finished_at = _now()
                db.commit()
            return

        with self._session_factory() as db:
            build = db.get(Build, build_id)
            for index, step in enumerate(steps):
                build.step_results.append(
                    BuildStep(
                        step_id=step.id,
                        name=step.name,
                        order_index=index,
                        status="pending",
                    )
                )
            db.commit()
            total = len(steps)

        final_status = "success"
        final_exit_code = 0

        for index, step in enumerate(steps, start=1):
            if abort_event.is_set():
                self._mark_remaining(build_id, from_index=index - 1, status="skipped")
                final_status = "aborted"
                break

            hub.write("")
            hub.write(f"────── [{index}/{total}] {step.name} ──────")

            with self._session_factory() as db:
                row = self._step_row(db, build_id, step.id)
                row.status = "running"
                row.started_at = _now()
                db.commit()

            result = run_command(
                command=step.command,
                shell=step.shell,
                workdir=workdir,
                env=step.env,
                timeout=timeout_seconds,
                hub=hub,
                abort_event=abort_event,
            )

            with self._session_factory() as db:
                row = self._step_row(db, build_id, step.id)
                row.finished_at = _now()
                row.exit_code = result.exit_code

                if result.aborted:
                    row.status = "aborted"
                    final_status = "aborted"
                elif result.timed_out:
                    row.status = "timeout"
                    final_status = "timeout"
                    hub.write(f"[timeout] 步骤超过 {timeout_seconds} 秒，已强制终止")
                elif result.error is not None or result.exit_code != 0:
                    row.status = "failed"
                    if final_status == "success":
                        final_status = "failed"
                        final_exit_code = result.exit_code or 1
                else:
                    row.status = "success"
                db.commit()

            if final_status in ("aborted", "timeout"):
                self._mark_remaining(build_id, from_index=index, status="skipped")
                break

            step_failed = result.error is not None or (result.exit_code or 0) != 0
            if step_failed and not (step.continue_on_failure or not fail_fast):
                self._mark_remaining(build_id, from_index=index, status="skipped")
                hub.write("步骤失败，按失败即停策略终止后续步骤。")
                break

        hub.write("")
        hub.write("=" * 60)
        hub.write(f"构建结束：{final_status}")

        with self._session_factory() as db:
            build = db.get(Build, build_id)
            build.status = final_status
            build.exit_code = final_exit_code
            build.finished_at = _now()
            db.commit()

        self._after_build(build_id, final_status)

    def _step_row(self, db: Session, build_id: int, step_id: int) -> BuildStep:
        return (
            db.query(BuildStep)
            .filter_by(build_id=build_id, step_id=step_id)
            .one()
        )

    def _mark_remaining(self, build_id: int, from_index: int, status: str) -> None:
        """把 from_index（含）之后的步骤标成 skipped。"""
        with self._session_factory() as db:
            rows = (
                db.query(BuildStep)
                .filter(BuildStep.build_id == build_id, BuildStep.order_index >= from_index)
                .all()
            )
            for row in rows:
                if row.status == "pending":
                    row.status = status
            db.commit()

    def _after_build(self, build_id: int, status: str) -> None:
        """构建结束后的收尾：清理信号、发通知，并保留 hub 供页面继续读。"""
        with self._lock:
            self._abort_events.pop(build_id, None)

        try:
            from .notify import notify_build_finished

            notify_build_finished(build_id, status)
        except Exception:  # noqa: BLE001  通知失败绝不影响构建结果
            pass
```

- [ ] **Step 5: 加一条 Build 的唯一约束验证**

在 `CI/tests/test_executor.py` 末尾追加：

```python
def test_build_numbers_are_unique_under_concurrent_triggers(executor, session, tmp_path):
    """并发触发不同任务时，各自编号不能乱。"""
    job_ids = [
        make_job(session, f"conc-{i}", [("echo hi", False)], tmp_path) for i in range(3)
    ]
    build_ids = [executor.trigger(j) for j in job_ids]

    numbers = [session.get(Build, b).build_number for b in build_ids]
    assert numbers == [1, 1, 1]

    for b in build_ids:
        wait_for_status(session, b)
```

- [ ] **Step 6: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_executor.py -v
```

预期：17 个测试全部 PASS。这个文件耗时较长（有多个真实的 `timeout /t` 等待），单次运行约 40–60 秒属正常。

- [ ] **Step 7: 跑一次全量测试**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

预期：全部 PASS。

- [ ] **Step 8: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner/executor.py CI/ci_runner/settings_store.py CI/tests/test_executor.py && git commit -m "feat(ci): 构建编排引擎（并发额度/失败即停/超时/中止）"
```

---

## Task 5: 任务 API

**Files:**
- Create: `CI/ci_runner/schemas.py`
- Create: `CI/ci_runner/api/jobs.py`
- Modify: `CI/ci_runner/main.py`（挂载 jobs 路由和 executor）
- Create: `CI/tests/test_api_jobs.py`

**Interfaces:**
- Consumes: `models`、`db.get_session`、`executor.Executor`、`executor.JobBusyError`、`scheduler.Scheduler`
- Produces:
  - Pydantic：`StepIn`、`StepOut`、`JobIn`、`JobOut`、`JobListItem`
  - `api/jobs.py` 的 `router`
  - `deps.get_executor() -> Executor`、`deps.get_scheduler() -> Scheduler`（放在 `CI/ci_runner/deps.py`，避免路由之间循环引用）

为了让 Task 5 能独立测试，scheduler 在这里先做成"接口已定、实现留到 Task 7"的占位会引入返工。改为：**Task 5 只依赖 executor，cron 校验用一个独立纯函数放在 `schemas.py` 里**（APScheduler 的 `CronTrigger.from_crontab` 现在就能用），Task 7 再把调度接上。

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_api_jobs.py`：

```python
"""任务 CRUD 与校验。"""

import pytest

from ci_runner.db import SessionLocal
from ci_runner.executor import Executor
from ci_runner.main import app


@pytest.fixture
def api_client():
    """带真实 executor 的测试客户端。"""
    from fastapi.testclient import TestClient

    ex = Executor(session_factory=SessionLocal)
    ex.start()
    app.state.executor = ex
    with TestClient(app) as c:
        yield c
    ex.shutdown()


def job_payload(**overrides):
    payload = {
        "name": "演示任务",
        "description": "测试用",
        "workdir": ".",
        "cron_expr": None,
        "timeout_seconds": 300,
        "fail_fast": True,
        "enabled": True,
        "steps": [
            {"name": "第一步", "command": "echo hello", "shell": "cmd"},
        ],
    }
    payload.update(overrides)
    return payload


def test_create_job(api_client, tmp_path):
    resp = api_client.post("/api/jobs", json=job_payload(workdir=str(tmp_path)))
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "演示任务"
    assert body["id"] > 0
    assert len(body["steps"]) == 1
    assert body["steps"][0]["order_index"] == 0


def test_create_job_missing_workdir_rejected(api_client):
    resp = api_client.post("/api/jobs", json=job_payload(workdir="D:/no/such/dir"))
    assert resp.status_code == 400
    assert "工作目录" in resp.json()["detail"]


def test_create_job_requires_at_least_one_step(api_client, tmp_path):
    resp = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path), steps=[])
    )
    assert resp.status_code == 400


def test_create_job_duplicate_name_rejected(api_client, tmp_path):
    api_client.post("/api/jobs", json=job_payload(workdir=str(tmp_path)))
    resp = api_client.post("/api/jobs", json=job_payload(workdir=str(tmp_path)))
    assert resp.status_code == 409


def test_create_job_invalid_cron_rejected(api_client, tmp_path):
    resp = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path), cron_expr="这不是cron")
    )
    assert resp.status_code == 400
    assert "cron" in resp.json()["detail"].lower()


def test_create_job_valid_cron_accepted(api_client, tmp_path):
    resp = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path), cron_expr="0 9 * * 1-5")
    )
    assert resp.status_code == 201


def test_list_jobs(api_client, tmp_path):
    api_client.post("/api/jobs", json=job_payload(workdir=str(tmp_path), name="A"))
    api_client.post("/api/jobs", json=job_payload(workdir=str(tmp_path), name="B"))

    resp = api_client.get("/api/jobs")
    assert resp.status_code == 200
    assert {j["name"] for j in resp.json()} == {"A", "B"}


def test_update_job_replaces_steps(api_client, tmp_path):
    created = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path))
    ).json()
    job_id = created["id"]

    payload = job_payload(
        workdir=str(tmp_path),
        steps=[
            {"name": "s0", "command": "echo 0", "shell": "cmd"},
            {"name": "s1", "command": "echo 1", "shell": "cmd"},
            {"name": "s2", "command": "echo 2", "shell": "cmd"},
        ],
    )
    resp = api_client.put(f"/api/jobs/{job_id}", json=payload)
    assert resp.status_code == 200

    detail = api_client.get(f"/api/jobs/{job_id}").json()
    assert [s["order_index"] for s in detail["steps"]] == [0, 1, 2]
    assert [s["name"] for s in detail["steps"]] == ["s0", "s1", "s2"]


def test_update_job_missing_returns_404(api_client, tmp_path):
    resp = api_client.put("/api/jobs/9999", json=job_payload(workdir=str(tmp_path)))
    assert resp.status_code == 404


def test_delete_job(api_client, tmp_path):
    created = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path))
    ).json()

    assert api_client.delete(f"/api/jobs/{created['id']}").status_code == 204
    assert api_client.get(f"/api/jobs/{created['id']}").status_code == 404


def test_delete_job_with_running_build_rejected(api_client, tmp_path):
    created = api_client.post(
        "/api/jobs",
        json=job_payload(
            workdir=str(tmp_path),
            steps=[{"name": "慢", "command": "timeout /t 6 >nul", "shell": "cmd"}],
        ),
    ).json()
    job_id = created["id"]

    import time

    build = api_client.post(f"/api/jobs/{job_id}/build").json()
    time.sleep(1.5)

    resp = api_client.delete(f"/api/jobs/{job_id}")
    assert resp.status_code == 409
    # 任务必须还在
    assert api_client.get(f"/api/jobs/{job_id}").status_code == 200

    api_client.post(f"/api/builds/{build['id']}/abort")


def test_manual_trigger_returns_202(api_client, tmp_path):
    created = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path))
    ).json()
    resp = api_client.post(f"/api/jobs/{created['id']}/build")
    assert resp.status_code == 202
    assert resp.json()["build_id"] > 0


def test_trigger_while_running_queues_then_rejects(api_client, tmp_path):
    """正在跑时再触发返回 202 排队；已有排队时第三次返回 409。"""
    created = api_client.post(
        "/api/jobs",
        json=job_payload(
            workdir=str(tmp_path),
            steps=[{"name": "慢", "command": "timeout /t 8 >nul", "shell": "cmd"}],
        ),
    ).json()
    job_id = created["id"]

    first = api_client.post(f"/api/jobs/{job_id}/build")
    assert first.status_code == 202

    second = api_client.post(f"/api/jobs/{job_id}/build")
    assert second.status_code == 202
    assert "排队" in second.json().get("detail", "") or second.json()["build_id"] > 0

    third = api_client.post(f"/api/jobs/{job_id}/build")
    assert third.status_code == 409

    api_client.post(f"/api/builds/{first.json()['build_id']}/abort")
    api_client.post(f"/api/builds/{second.json()['build_id']}/abort")


def test_validate_cron_endpoint(api_client):
    ok = api_client.post("/api/jobs/validate-cron", json={"cron_expr": "*/30 * * * *"})
    assert ok.status_code == 200
    assert len(ok.json()["next_runs"]) == 5

    bad = api_client.post("/api/jobs/validate-cron", json={"cron_expr": "nonsense"})
    assert bad.status_code == 400


def test_timeout_out_of_range_rejected(api_client, tmp_path):
    resp = api_client.post(
        "/api/jobs", json=job_payload(workdir=str(tmp_path), timeout_seconds=5)
    )
    assert resp.status_code == 422
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_api_jobs.py -v
```

预期：全部 FAIL（404，因为路由还没挂）。

- [ ] **Step 3: 写 Pydantic 模型**

创建 `CI/ci_runner/schemas.py`：

```python
"""请求/响应模型，以及 cron 表达式校验。"""

from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel, ConfigDict, Field, field_validator

from . import config


def parse_cron(expr: str):
    """把 5 段 cron 表达式解析成 CronTrigger，非法则抛 ValueError。"""
    try:
        return CronTrigger.from_crontab(expr)
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError(f"cron 表达式无法解析：{expr}（{exc}）") from exc


def next_runs(expr: str, count: int = 5) -> list[datetime]:
    """算出接下来 count 次触发时间。"""
    trigger = parse_cron(expr)
    now = datetime.now()
    result = []
    previous = now
    for _ in range(count):
        nxt = trigger.get_next_fire_time(None, previous)
        if nxt is None:
            break
        result.append(nxt)
        previous = nxt
    return result


class StepIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    command: str = Field(min_length=1, max_length=4000)
    shell: str = Field(default="cmd", pattern="^(cmd|powershell)$")
    continue_on_failure: bool = False
    env: dict[str, str] | None = None


class StepOut(StepIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_index: int


class JobIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    workdir: str = Field(min_length=1, max_length=500)
    cron_expr: str | None = Field(default=None, max_length=100)
    timeout_seconds: int = Field(
        default=config.DEFAULT_TIMEOUT_SECONDS,
        ge=config.MIN_TIMEOUT_SECONDS,
        le=config.MAX_TIMEOUT_SECONDS,
    )
    fail_fast: bool = True
    enabled: bool = True
    steps: list[StepIn] = Field(min_length=1)

    @field_validator("cron_expr")
    @classmethod
    def _check_cron(cls, value):
        if value is None or value.strip() == "":
            return None
        parse_cron(value.strip())
        return value.strip()


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    workdir: str
    cron_expr: str | None
    timeout_seconds: int
    fail_fast: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime
    steps: list[StepOut] = []


class BuildSummary(BaseModel):
    """嵌在任务列表里的最近一次构建摘要。"""

    # 赋值时来源是 Build ORM 对象，必须允许按属性读取
    model_config = ConfigDict(from_attributes=True)

    id: int
    build_number: int
    status: str
    trigger: str
    started_at: datetime | None
    finished_at: datetime | None


class JobListItem(JobOut):
    last_build: BuildSummary | None = None


class CronCheckIn(BaseModel):
    cron_expr: str


class CronCheckOut(BaseModel):
    next_runs: list[datetime]


class TriggerOut(BaseModel):
    build_id: int
    build_number: int
```

- [ ] **Step 4: 写依赖注入模块**

创建 `CI/ci_runner/deps.py`：

```python
"""跨路由共享的依赖。

放在独立模块里是为了让 api/jobs.py 和 api/builds.py 都能拿到
executor / scheduler，而不用互相 import。
"""

from fastapi import Request

from .executor import Executor
from .scheduler import Scheduler


def get_executor(request: Request) -> Executor:
    return request.app.state.executor


def get_scheduler(request: Request) -> Scheduler:
    return request.app.state.scheduler
```

`deps.py` 引用了 `scheduler`，所以 Task 5 需要 Task 7 的 `Scheduler` 类先存在。为避免在 Task 5 里写一次性占位代码，**把 Task 7 的 `scheduler.py` 骨架提前到 Task 5 一起创建**：`Scheduler` 类此时只有空实现（`start`/`shutdown`/`sync_job`/`remove_job` 都是空方法），Task 7 再填实现并补测试。

- [ ] **Step 5: 写 scheduler 骨架**

创建 `CI/ci_runner/scheduler.py`：

```python
"""APScheduler 封装。

任务 5 阶段只需要这个类的形状存在，真正的实现和测试在任务 7。
"""

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class Scheduler:
    def __init__(self, executor, session_factory):
        self._executor = executor
        self._session_factory = session_factory
        self._sched = BackgroundScheduler()

    def start(self) -> None:
        self._sched.start()

    def shutdown(self) -> None:
        if self._sched.running:
            self._sched.shutdown(wait=False)

    def sync_job(self, job) -> None:
        """按任务的当前配置增删改对应的调度项。"""

    def remove_job(self, job_id: int) -> None:
        """删除任务时移除调度项。"""

    def _fire(self, job_id: int) -> None:
        """定时触发入口。"""
```

- [ ] **Step 6: 写任务路由**

创建 `CI/ci_runner/api/jobs.py`：

```python
"""任务 CRUD、手动触发、cron 校验。"""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_session
from ..deps import get_executor, get_scheduler
from ..executor import Executor, JobBusyError
from ..models import Build, Job, Step
from ..schemas import (
    CronCheckIn,
    CronCheckOut,
    JobIn,
    JobListItem,
    JobOut,
    TriggerOut,
    next_runs,
)

router = APIRouter()


def _validate_workdir(workdir: str) -> str:
    if not os.path.isdir(workdir):
        raise HTTPException(status_code=400, detail=f"工作目录不存在或不是目录：{workdir}")
    return workdir


def _get_job_or_404(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"任务不存在：{job_id}")
    return job


def _apply(db: Session, job: Job, payload: JobIn) -> None:
    """把请求体写进 Job 和它的步骤。

    步骤采用整体替换语义：删旧插新。一个事务完成，不会出现顺序错乱。
    """
    job.name = payload.name
    job.description = payload.description
    job.workdir = payload.workdir
    job.cron_expr = payload.cron_expr
    job.timeout_seconds = payload.timeout_seconds
    job.fail_fast = payload.fail_fast
    job.enabled = payload.enabled

    job.steps.clear()
    db.flush()
    for index, step in enumerate(payload.steps):
        job.steps.append(
            Step(
                order_index=index,
                name=step.name,
                command=step.command,
                shell=step.shell,
                continue_on_failure=step.continue_on_failure,
                env=step.env,
            )
        )


@router.get("/jobs", response_model=list[JobListItem])
def list_jobs(db: Session = Depends(get_session)):
    jobs = db.query(Job).order_by(Job.id).all()
    items = []
    for job in jobs:
        last = (
            db.query(Build)
            .filter_by(job_id=job.id)
            .order_by(Build.build_number.desc())
            .first()
        )
        item = JobListItem.model_validate(job)
        if last is not None:
            item.last_build = last
        items.append(item)
    return items


@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobIn,
    db: Session = Depends(get_session),
    scheduler=Depends(get_scheduler),
):
    _validate_workdir(payload.workdir)
    if db.query(Job).filter_by(name=payload.name).first() is not None:
        raise HTTPException(status_code=409, detail=f"任务名已存在：{payload.name}")

    job = Job()
    _apply(db, job, payload)
    db.add(job)
    db.commit()
    db.refresh(job)
    scheduler.sync_job(job)
    return job


@router.post("/jobs/validate-cron", response_model=CronCheckOut)
def validate_cron(payload: CronCheckIn):
    """校验 cron 表达式并给出接下来 5 次触发时间。

    必须定义在 get_job 之前：FastAPI 按注册顺序匹配路由，
    否则 /jobs/validate-cron 会先被 /jobs/{job_id} 截住。
    """
    try:
        runs = next_runs(payload.cron_expr, count=5)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CronCheckOut(next_runs=runs)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_session)):
    return _get_job_or_404(db, job_id)


@router.put("/jobs/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    payload: JobIn,
    db: Session = Depends(get_session),
    scheduler=Depends(get_scheduler),
):
    job = _get_job_or_404(db, job_id)
    _validate_workdir(payload.workdir)

    clash = db.query(Job).filter(Job.name == payload.name, Job.id != job_id).first()
    if clash is not None:
        raise HTTPException(status_code=409, detail=f"任务名已存在：{payload.name}")

    _apply(db, job, payload)
    db.commit()
    db.refresh(job)
    scheduler.sync_job(job)
    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_session),
    scheduler=Depends(get_scheduler),
):
    job = _get_job_or_404(db, job_id)

    # 有构建在跑或排队时不允许删除，否则子进程会变成孤儿
    active = (
        db.query(Build)
        .filter(Build.job_id == job_id, Build.status.in_(["running", "queued"]))
        .first()
    )
    if active is not None:
        raise HTTPException(
            status_code=409,
            detail=f"该任务有构建正在{'运行' if active.status == 'running' else '排队'}，请先中止再删除",
        )

    scheduler.remove_job(job_id)
    db.delete(job)
    db.commit()


@router.post(
    "/jobs/{job_id}/build",
    response_model=TriggerOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_build(
    job_id: int,
    db: Session = Depends(get_session),
    executor: Executor = Depends(get_executor),
):
    _get_job_or_404(db, job_id)
    try:
        build_id = executor.trigger(job_id, trigger="manual")
    except JobBusyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    build = db.get(Build, build_id)
    return TriggerOut(build_id=build_id, build_number=build.build_number)


@router.get("/jobs/{job_id}/builds")
def job_builds(
    job_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_session),
):
    _get_job_or_404(db, job_id)
    rows = (
        db.query(Build)
        .filter_by(job_id=job_id)
        .order_by(Build.build_number.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": b.id,
            "build_number": b.build_number,
            "status": b.status,
            "trigger": b.trigger,
            "started_at": b.started_at,
            "finished_at": b.finished_at,
            "created_at": b.created_at,
        }
        for b in rows
    ]


```

**注意：`validate_cron` 的位置不能动。** 它必须定义在 `get_job` 之前——FastAPI 按注册顺序匹配路由，放在后面的话 `/jobs/validate-cron` 会先被 `/jobs/{job_id}` 截住，`job_id="validate-cron"` 转 int 失败返回 422。

- [ ] **Step 7: 挂载路由**

修改 `CI/ci_runner/main.py`，替换为：

```python
"""FastAPI 应用装配与启动入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import config
from .api import jobs, misc
from .db import SessionLocal, init_db
from .deps import get_executor
from .executor import Executor
from .scheduler import Scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    executor = getattr(app.state, "executor", None)
    if executor is None:
        executor = Executor(session_factory=SessionLocal)
        app.state.executor = executor
    executor.start()

    scheduler = Scheduler(executor=executor, session_factory=SessionLocal)
    app.state.scheduler = scheduler
    scheduler.start()

    yield

    scheduler.shutdown()
    executor.shutdown()


app = FastAPI(title="CI Runner", version=config.APP_VERSION, lifespan=lifespan)

app.include_router(misc.router, prefix="/api", tags=["misc"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
```

`getattr(app.state, "executor", None)` 的分支是给测试用的：测试可以在进入 `TestClient` 前把 `app.state.executor` 换成自己的实例。

- [ ] **Step 8: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_api_jobs.py -v
```

预期：15 个测试全部 PASS。

- [ ] **Step 9: 跑一次全量测试并提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner && git commit -m "feat(ci): 任务 CRUD、手动触发与 cron 校验接口"
```

---

## Task 6: 构建 API（详情、日志、SSE、中止、下载）

**Files:**
- Create: `CI/ci_runner/api/builds.py`
- Modify: `CI/ci_runner/main.py`（挂载 builds 路由）
- Create: `CI/tests/test_api_builds.py`

**Interfaces:**
- Consumes: `executor.Executor`、`loghub.LogHub`、`loghub.read_log_file`、`models`
- Produces: `api/builds.py` 的 `router`

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_api_builds.py`：

```python
"""构建详情、日志增量、SSE、中止、下载。"""

import time

import pytest

from ci_runner.db import SessionLocal
from ci_runner.executor import Executor
from ci_runner.main import app


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    ex = Executor(session_factory=SessionLocal)
    ex.start()
    app.state.executor = ex
    with TestClient(app) as c:
        yield c
    ex.shutdown()


def make_job_via_api(api_client, tmp_path, name, commands, **overrides):
    payload = {
        "name": name,
        "description": "",
        "workdir": str(tmp_path),
        "cron_expr": None,
        "timeout_seconds": 300,
        "fail_fast": True,
        "enabled": True,
        "steps": [
            {"name": f"步骤{i}", "command": c, "shell": "cmd"}
            for i, c in enumerate(commands)
        ],
    }
    payload.update(overrides)
    resp = api_client.post("/api/jobs", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def wait_done(api_client, build_id, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        body = api_client.get(f"/api/builds/{build_id}").json()
        if body["status"] not in ("queued", "running"):
            return body
        time.sleep(0.1)
    raise AssertionError("构建未在预期时间内结束")


def test_build_detail_includes_steps(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "detail", ["echo a", "echo b"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]
    body = wait_done(api_client, build_id)

    assert body["status"] == "success"
    assert [s["name"] for s in body["steps"]] == ["步骤0", "步骤1"]
    assert all(s["status"] == "success" for s in body["steps"])
    assert body["started_at"] is not None
    assert body["finished_at"] is not None


def test_build_detail_404(api_client):
    assert api_client.get("/api/builds/99999").status_code == 404


def test_log_incremental_fetch(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "loginc", ["echo 第一行"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]
    wait_done(api_client, build_id)

    first = api_client.get(f"/api/builds/{build_id}/log?offset=0").json()
    assert first["next_offset"] > 0
    assert any("第一行" in line for line in first["lines"])

    second = api_client.get(
        f"/api/builds/{build_id}/log?offset={first['next_offset']}"
    ).json()
    assert second["lines"] == []


def test_log_fetch_after_hub_evicted_uses_file(api_client, tmp_path):
    """构建结束后即使内存缓冲没了，也要能从文件读到日志。"""
    job_id = make_job_via_api(api_client, tmp_path, "filelog", ["echo 从文件读"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]
    wait_done(api_client, build_id)

    # 模拟内存缓冲已释放
    app.state.executor._hubs.pop(build_id, None)

    body = api_client.get(f"/api/builds/{build_id}/log?offset=0").json()
    assert any("从文件读" in line for line in body["lines"])


def test_sse_stream_emits_log_and_end_events(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "sse", ["echo sse-内容"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]

    events = []
    with api_client.stream("GET", f"/api/builds/{build_id}/stream") as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        for line in resp.iter_lines():
            events.append(line)
            if len(events) > 400:
                break
            if any(e.startswith("event: end") for e in events[-3:]):
                break

    text = "\n".join(events)
    assert "event: log" in text
    assert "sse-内容" in text
    assert "event: end" in text


def test_abort_finished_build_returns_409(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "abortdone", ["echo hi"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]
    wait_done(api_client, build_id)

    resp = api_client.post(f"/api/builds/{build_id}/abort")
    assert resp.status_code == 409


def test_abort_running_build(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "abortrun", ["timeout /t 30 >nul"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if api_client.get(f"/api/builds/{build_id}").json()["status"] == "running":
            break
        time.sleep(0.05)

    assert api_client.post(f"/api/builds/{build_id}/abort").status_code == 200
    assert wait_done(api_client, build_id)["status"] == "aborted"


def test_download_log(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "download", ["echo 下载内容"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]
    wait_done(api_client, build_id)

    resp = api_client.get(f"/api/builds/{build_id}/download")
    assert resp.status_code == 200
    assert "attachment" in resp.headers["content-disposition"]
    assert "下载内容" in resp.content.decode("utf-8")


def test_queue_endpoint(api_client, tmp_path):
    job_id = make_job_via_api(api_client, tmp_path, "queueq", ["timeout /t 3 >nul"])
    build_id = api_client.post(f"/api/jobs/{job_id}/build").json()["build_id"]

    time.sleep(1)
    body = api_client.get("/api/queue").json()
    assert body["running_count"] >= 1
    assert any(b["id"] == build_id for b in body["running"])

    api_client.post(f"/api/builds/{build_id}/abort")


def test_settings_endpoints(api_client):
    body = api_client.get("/api/settings").json()
    assert body["max_workers"] == "4"

    resp = api_client.put("/api/settings", json={"max_workers": "2"})
    assert resp.status_code == 200
    assert api_client.get("/api/settings").json()["max_workers"] == "2"


def test_settings_rejects_out_of_range(api_client):
    resp = api_client.put("/api/settings", json={"max_workers": "99"})
    assert resp.status_code == 400
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_api_builds.py -v
```

预期：全部 FAIL（404）。

- [ ] **Step 3: 实现构建路由**

创建 `CI/ci_runner/api/builds.py`：

```python
"""构建详情、日志增量拉取、SSE 实时日志、中止、下载。

日志有两条来源：正在跑的构建走内存 LogHub，已结束且缓冲被回收的走日志文件。
两条路都返回同样的 {lines, next_offset, truncated} 结构，前端不用区分。
"""

import json
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..db import SessionLocal, get_session
from ..deps import get_executor
from ..executor import Executor
from ..loghub import read_log_file
from ..models import Build, BuildStep

router = APIRouter()

# SSE 连接可能持续很久，不能像普通请求那样从头到尾占一个 Session，
# 所以生成器每一轮自己开一个短命会话。
SessionLocalScoped = SessionLocal

# SSE 在服务端轮询日志的间隔
_STREAM_POLL = 0.2
# 单条 SSE 连接的最长寿命，防止浏览器不关连接时线程永久占用
_STREAM_MAX_SECONDS = 3600
# 已结束的构建：一次性推完就断开
_TERMINAL = {"success", "failed", "aborted", "timeout"}


def _get_build_or_404(db: Session, build_id: int) -> Build:
    build = db.get(Build, build_id)
    if build is None:
        raise HTTPException(status_code=404, detail=f"构建不存在：{build_id}")
    return build


def _read_log(build: Build, executor: Executor, offset: int) -> dict:
    hub = executor.get_hub(build.id)
    if hub is not None:
        return hub.snapshot(offset)
    return read_log_file(Path(build.log_path), offset)


@router.get("/builds/{build_id}")
def get_build(build_id: int, db: Session = Depends(get_session)):
    build = _get_build_or_404(db, build_id)
    steps = (
        db.query(BuildStep)
        .filter_by(build_id=build_id)
        .order_by(BuildStep.order_index)
        .all()
    )
    return {
        "id": build.id,
        "job_id": build.job_id,
        "job_name": build.job.name,
        "build_number": build.build_number,
        "status": build.status,
        "trigger": build.trigger,
        "exit_code": build.exit_code,
        "error_message": build.error_message,
        "started_at": build.started_at,
        "finished_at": build.finished_at,
        "created_at": build.created_at,
        "steps": [
            {
                "id": s.id,
                "name": s.name,
                "order_index": s.order_index,
                "status": s.status,
                "exit_code": s.exit_code,
                "started_at": s.started_at,
                "finished_at": s.finished_at,
            }
            for s in steps
        ],
    }


@router.get("/builds/{build_id}/log")
def get_log(
    build_id: int,
    offset: int = 0,
    db: Session = Depends(get_session),
    executor: Executor = Depends(get_executor),
):
    build = _get_build_or_404(db, build_id)
    result = _read_log(build, executor, offset)
    result["status"] = build.status
    return result


@router.get("/builds/{build_id}/stream")
def stream_log(
    build_id: int,
    offset: int = 0,
    db: Session = Depends(get_session),
    executor: Executor = Depends(get_executor),
):
    build = _get_build_or_404(db, build_id)

    def event(name: str, payload) -> str:
        return f"event: {name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def generator():
        position = offset
        deadline = time.monotonic() + _STREAM_MAX_SECONDS

        while True:
            with SessionLocalScoped() as session:
                current = session.get(Build, build_id)
                if current is None:
                    yield event("end", {"status": "deleted"})
                    return
                status = current.status
                snapshot = _read_log(current, executor, position)

            for line in snapshot["lines"]:
                yield event("log", line)
            position = snapshot["next_offset"]

            if snapshot["truncated"]:
                yield event("truncated", {"next_offset": position})

            yield event("status", {"status": status})

            # 已结束的构建：推完剩余日志就收尾
            if status in _TERMINAL:
                yield event("end", {"status": status})
                return

            if time.monotonic() > deadline:
                yield event("end", {"status": "stream-timeout"})
                return

            time.sleep(_STREAM_POLL)

    return StreamingResponse(generator(), media_type="text/event-stream")


@router.post("/builds/{build_id}/abort")
def abort_build(
    build_id: int,
    db: Session = Depends(get_session),
    executor: Executor = Depends(get_executor),
):
    build = _get_build_or_404(db, build_id)
    if build.status in _TERMINAL:
        raise HTTPException(
            status_code=409, detail=f"构建已结束（{build.status}），无法中止"
        )
    executor.abort(build_id)
    return {"ok": True}


@router.get("/builds/{build_id}/download")
def download_log(
    build_id: int,
    db: Session = Depends(get_session),
):
    build = _get_build_or_404(db, build_id)
    path = Path(build.log_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="日志文件不存在")
    return FileResponse(
        path,
        media_type="text/plain; charset=utf-8",
        filename=f"build-{build.job_id}-{build.build_number}.log",
    )
```

`get_log` 走的是请求级 `db`，不受上面的短命会话影响。

- [ ] **Step 4: 挂载路由**

修改 `CI/ci_runner/main.py`：在 `from .api import jobs, misc` 后加上 `builds`，并追加一行 `include_router`：

```python
from .api import builds, jobs, misc
```

```python
app.include_router(builds.router, prefix="/api", tags=["builds"])
```

- [ ] **Step 5: 实现队列与设置接口**

修改 `CI/ci_runner/api/misc.py`，替换为：

```python
"""队列、设置、健康检查接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import config
from ..db import get_session
from ..deps import get_executor
from ..executor import Executor
from ..models import Build, Job
from ..settings_store import all_settings, get_int_setting, set_setting

router = APIRouter()


@router.get("/health")
def health(executor: Executor = Depends(get_executor)):
    """给 start.bat 判断服务是否就绪用。"""
    return {
        "status": "ok",
        "version": config.APP_VERSION,
        "running_count": executor.running_count(),
    }


def _build_brief(db: Session, build: Build) -> dict:
    job = db.get(Job, build.job_id)
    return {
        "id": build.id,
        "job_id": build.job_id,
        "job_name": job.name if job else "?",
        "build_number": build.build_number,
        "status": build.status,
        "trigger": build.trigger,
        "started_at": build.started_at,
    }


@router.get("/queue")
def queue(
    db: Session = Depends(get_session),
    executor: Executor = Depends(get_executor),
):
    running_ids = [b.id for b in db.query(Build).filter_by(status="running").all()]
    queued_ids = executor.queued_ids()

    running = [_build_brief(db, db.get(Build, i)) for i in running_ids if db.get(Build, i)]
    queued = [_build_brief(db, db.get(Build, i)) for i in queued_ids if db.get(Build, i)]

    return {
        "running_count": len(running),
        "queued_count": len(queued),
        "max_workers": get_int_setting(db, "max_workers"),
        "running": running,
        "queued": queued,
    }


@router.get("/settings")
def read_settings(db: Session = Depends(get_session)):
    return all_settings(db)


@router.put("/settings")
def update_settings(payload: dict, db: Session = Depends(get_session)):
    from ..settings_store import DEFAULTS

    for key, value in payload.items():
        if key not in DEFAULTS:
            raise HTTPException(status_code=400, detail=f"未知设置项：{key}")
        if key == "max_workers":
            try:
                number = int(value)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="max_workers 必须是整数") from None
            if not (config.MIN_MAX_WORKERS <= number <= config.MAX_MAX_WORKERS):
                raise HTTPException(
                    status_code=400,
                    detail=f"max_workers 必须在 {config.MIN_MAX_WORKERS}~{config.MAX_MAX_WORKERS} 之间",
                )
            value = str(number)
        elif key.startswith("notify_"):
            if str(value) not in ("0", "1"):
                raise HTTPException(status_code=400, detail=f"{key} 只能是 0 或 1")
            value = str(value)
        set_setting(db, key, str(value))

    db.commit()
    return all_settings(db)
```

- [ ] **Step 6: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_api_builds.py -v
```

预期：11 个测试全部 PASS。

如果 `test_sse_stream_emits_log_and_end_events` 卡住，检查 `_STREAM_POLL` 和生成器的退出条件——构建结束后必须能走到 `event: end` 并 `return`。

- [ ] **Step 7: 跑全量测试并提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner && git commit -m "feat(ci): 构建详情、日志增量、SSE 实时流、中止与下载接口"
```

---

## Task 7: cron 调度

把 Task 5 建立起来的 `Scheduler` 骨架填成真实现。

**Files:**
- Modify: `CI/ci_runner/scheduler.py`
- Create: `CI/tests/test_scheduler.py`

**Interfaces:**
- Consumes: `executor.Executor.trigger`、`executor.JobBusyError`、`models.Job`、`schemas.parse_cron`
- Produces: `Scheduler.start()` / `.shutdown()` / `.sync_job(job)` / `.remove_job(job_id)` / `.job_ids() -> list[str]`（测试用）

- [ ] **Step 1: 写失败的测试*

创建 `CI/tests/test_scheduler.py`：

```python
"""调度同步与跳过策略。"""

import time

import pytest

from ci_runner.db import SessionLocal
from ci_runner.executor import Executor
from ci_runner.models import Build, Job, Step
from ci_runner.scheduler import Scheduler


@pytest.fixture
def executor():
    ex = Executor(session_factory=SessionLocal)
    ex.start()
    yield ex
    ex.shutdown()


@pytest.fixture
def scheduler(executor):
    sch = Scheduler(executor=executor, session_factory=SessionLocal)
    sch.start()
    yield sch
    sch.shutdown()


def make_job(session, name, cron_expr=None, enabled=True, command="echo hi"):
    job = Job(name=name, workdir=".", cron_expr=cron_expr, enabled=enabled)
    job.steps = [Step(order_index=0, name="s", command=command, shell="cmd")]
    session.add(job)
    session.commit()
    return job


def test_disabled_job_is_not_scheduled(scheduler, session):
    job = make_job(session, "off", cron_expr="*/5 * * * *", enabled=False)
    scheduler.sync_job(job)
    assert scheduler.job_ids() == []


def test_job_without_cron_is_not_scheduled(scheduler, session):
    job = make_job(session, "nocron", cron_expr=None)
    scheduler.sync_job(job)
    assert scheduler.job_ids() == []


def test_enabled_job_with_cron_is_scheduled(scheduler, session):
    job = make_job(session, "on", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)
    assert scheduler.job_ids() == [f"job_{job.id}"]


def test_sync_is_idempotent(scheduler, session):
    job = make_job(session, "idem", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)
    scheduler.sync_job(job)
    assert scheduler.job_ids() == [f"job_{job.id}"]


def test_changing_cron_reschedules(scheduler, session):
    job = make_job(session, "resched", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)

    job.cron_expr = "0 3 * * *"
    session.commit()
    scheduler.sync_job(job)

    assert scheduler.job_ids() == [f"job_{job.id}"]
    trigger = scheduler._sched.get_job(f"job_{job.id}").trigger
    assert str(trigger) == str(__import__("apscheduler.triggers.cron", fromlist=["CronTrigger"]).CronTrigger.from_crontab("0 3 * * *"))


def test_disabling_removes_schedule(scheduler, session):
    job = make_job(session, "toggle", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)
    assert scheduler.job_ids() != []

    job.enabled = False
    session.commit()
    scheduler.sync_job(job)
    assert scheduler.job_ids() == []


def test_remove_job(scheduler, session):
    job = make_job(session, "rm", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)

    scheduler.remove_job(job.id)
    assert scheduler.job_ids() == []


def test_fire_triggers_build(scheduler, session):
    job = make_job(session, "fire", cron_expr="*/5 * * * *")
    scheduler.sync_job(job)

    scheduler._fire(job.id)

    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        session.expire_all()
        build = session.query(Build).filter_by(job_id=job.id).first()
        if build is not None and build.status not in ("queued", "running"):
            break
        time.sleep(0.1)

    session.expire_all()
    build = session.query(Build).filter_by(job_id=job.id).first()
    assert build is not None
    assert build.trigger == "cron"
    assert build.build_number == 1


def test_fire_skipped_when_build_already_running(scheduler, session, caplog):
    """已有构建在跑时，定时触发必须被跳过，且不产生新构建记录。"""
    job = make_job(session, "skipme", cron_expr="*/5 * * * *", command="timeout /t 4 >nul")
    scheduler.sync_job(job)

    scheduler._fire(job.id)
    time.sleep(1.0)

    before = session.query(Build).filter_by(job_id=job.id).count()
    scheduler._fire(job.id)
    time.sleep(0.5)
    session.expire_all()
    after = session.query(Build).filter_by(job_id=job.id).count()

    assert after == before, "定时触发不该在已有构建时新增构建记录"
    assert "skip" in caplog.text.lower()

    for build in session.query(Build).filter_by(job_id=job.id).all():
        scheduler._executor.abort(build.id)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_scheduler.py -v
```

预期：全部 FAIL（骨架是空实现）。

- [ ] **Step 3: 实现 scheduler.py**

替换 `CI/ci_runner/scheduler.py`：

```python
"""APScheduler 封装：按任务的 cron 配置同步调度项。

只负责"什么时候投递"，不关心构建怎么跑。
"""

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .executor import JobBusyError
from .models import Job
from .schemas import parse_cron

log = logging.getLogger("ci_runner.scheduler")


class Scheduler:
    def __init__(self, executor, session_factory):
        self._executor = executor
        self._session_factory = session_factory
        self._sched = BackgroundScheduler()

    # ---------- 生命周期 ----------

    def start(self) -> None:
        self._sched.start()
        self.reload_all()

    def shutdown(self) -> None:
        if getattr(self._sched, "running", False):
            self._sched.shutdown(wait=False)

    def reload_all(self) -> None:
        """启动时把库里所有该调度的任务注册上。"""
        with self._session_factory() as db:
            jobs = db.query(Job).all()
            for job in jobs:
                self.sync_job(job, db=db)

    # ---------- 同步 ----------

    def sync_job(self, job, db=None) -> None:
        """按任务当前配置增删改调度项。任务对象必须已 commit。"""
        job_id = job.id
        key = f"job_{job_id}"

        should_schedule = bool(job.enabled and job.cron_expr)

        if not should_schedule:
            if self._sched.get_job(key) is not None:
                self._sched.remove_job(key)
            return

        trigger = CronTrigger.from_crontab(job.cron_expr)
        if self._sched.get_job(key) is None:
            self._sched.add_job(
                self._fire,
                trigger=trigger,
                args=[job_id],
                id=key,
                replace_existing=True,
                misfire_grace_time=60,
            )
        else:
            self._sched.reschedule_job(key, trigger=trigger)

    def remove_job(self, job_id: int) -> None:
        key = f"job_{job_id}"
        if self._sched.get_job(key) is not None:
            self._sched.remove_job(key)

    def job_ids(self) -> list[str]:
        """当前已注册的调度项 ID，测试用。"""
        return [j.id for j in self._sched.get_jobs()]

    # ---------- 触发 ----------

    def _fire(self, job_id: int) -> None:
        """定时触发入口。

        已有构建在跑或排队时跳过本次触发——不排队，否则一个
        5 分钟一次、每次跑 10 分钟的任务会积压到失控。
        跳过不产生任何构建记录，只写应用日志。
        """
        try:
            build_id = self._executor.trigger(job_id, trigger="cron")
            log.info("cron 触发 job=%s build=%s", job_id, build_id)
        except JobBusyError:
            log.info("skip job=%s 已有构建在运行或排队", job_id)
        except ValueError as exc:
            log.warning("cron 触发失败 job=%s：%s", job_id, exc)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_scheduler.py -v
```

预期：9 个测试全部 PASS。

- [ ] **Step 5: 跑全量测试并提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner/scheduler.py CI/tests/test_scheduler.py && git commit -m "feat(ci): cron 调度（同步/跳过已运行的触发）"
```

---

## Task 8: Windows 桌面通知

**Files:**
- Create: `CI/ci_runner/notify.py`
- Create: `CI/tests/test_notify.py`

**Interfaces:**
- Consumes: `models.Build`、`models.Job`、`settings_store.get_bool_setting`
- Produces:
  - `should_notify(db, trigger: str, status: str) -> bool`
  - `notify(title: str, body: str) -> bool`（返回是否成功弹出 Toast）
  - `notify_build_finished(build_id: int) -> None`（executor 回调入口）

**设计要点：** 通知绝不能影响构建结果——`notify_build_finished` 内部把所有异常吞掉。

- [ ] **Step 1: 写失败的测试**

创建 `CI/tests/test_notify.py`：

```python
"""通知策略与失败隔离。"""

from ci_runner.models import Build, Job
from ci_runner.notify import notify_build_finished, should_notify
from ci_runner.settings_store import set_setting


def test_failure_always_notifies(session):
    assert should_notify(session, trigger="cron", status="failed") is True
    assert should_notify(session, trigger="manual", status="failed") is True


def test_timeout_always_notifies(session):
    assert should_notify(session, trigger="cron", status="timeout") is True


def test_manual_success_notifies_by_default(session):
    assert should_notify(session, trigger="manual", status="success") is True


def test_cron_success_does_not_notify_by_default(session):
    """定时任务成功不通知，否则每天早上必弹一次。"""
    assert should_notify(session, trigger="cron", status="success") is False


def test_cron_success_notifies_when_enabled(session):
    set_setting(session, "notify_on_success_cron", "1")
    session.commit()
    assert should_notify(session, trigger="cron", status="success") is True


def test_notifications_can_be_disabled(session):
    set_setting(session, "notify_on_failure", "0")
    session.commit()
    assert should_notify(session, trigger="manual", status="failed") is False


def test_notify_build_finished_swallows_errors(session, monkeypatch):
    """即使底层弹窗炸了，也不能把异常抛出来影响构建。"""
    import ci_runner.notify as notify_module

    job = Job(name="n", workdir=".")
    session.add(job)
    session.commit()
    build = Build(job_id=job.id, build_number=1, status="failed")
    session.add(build)
    session.commit()

    def boom(*args, **kwargs):
        raise RuntimeError("通知炸了")

    monkeypatch.setattr(notify_module, "_show_toast", boom)
    # 不抛异常即为通过
    notify_build_finished(build.id)


def test_notify_build_finished_unknown_id_is_noop(session):
    notify_build_finished(999999)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_notify.py -v
```

预期：全部 FAIL，`ModuleNotFoundError: No module named 'ci_runner.notify'`。

- [ ] **Step 3: 实现 notify.py**

创建 `CI/ci_runner/notify.py`：

```python
"""Windows 桌面通知。

主方案走 PowerShell 调 WinRT 的 Toast API——不需要安装任何 Python 包。
失败则降级到系统提示音。通知失败绝不影响构建结果。
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from .db import SessionLocal
from .models import Build, Job
from .settings_store import get_bool_setting

log = logging.getLogger("ci_runner.notify")

_CREATE_NO_WINDOW = 0x08000000

# 用 PowerShell 直接调 WinRT，避免依赖 BurntToast 之类的第三方模块
_TOAST_PS = """$ErrorActionPreference = 'Stop'
[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime]
[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime]
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml(@'
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{title}</text>
      <text>{body}</text>
    </binding>
  </visual>
</toast>
'@)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('CI Runner').Show($toast)
"""

_STATUS_ICON = {
    "success": "✅",
    "failed": "❌",
    "timeout": "⏱",
    "aborted": "⛔",
}
_STATUS_TEXT = {
    "success": "构建成功",
    "failed": "构建失败",
    "timeout": "构建超时",
    "aborted": "构建已中止",
}


def should_notify(db, trigger: str, status: str) -> bool:
    """按设置决定这次构建要不要弹通知。"""
    if status in ("failed", "timeout", "aborted"):
        return get_bool_setting(db, "notify_on_failure")

    if status == "success":
        if trigger == "cron":
            return get_bool_setting(db, "notify_on_success_cron")
        return get_bool_setting(db, "notify_on_success_manual")

    return False


def _show_toast(title: str, body: str) -> bool:
    """弹一个 Windows Toast。成功返回 True。"""
    script = _TOAST_PS.replace("{title}", escape(title)).replace("{body}", escape(body))

    fd, path = tempfile.mkstemp(suffix=".ps1", prefix="ci_runner_toast_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            f.write(script)

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                path,
            ],
            capture_output=True,
            timeout=15,
            creationflags=_CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            log.debug("Toast 失败：%s", result.stderr.decode("utf-8", errors="replace")[:300])
            return False
        return True
    finally:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass


def _fallback_beep() -> None:
    """Toast 不可用时的降级：播放系统提示音。"""
    try:
        import winsound

        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:  # noqa: BLE001
        pass


def notify(title: str, body: str) -> bool:
    """发通知。Toast 失败则退回提示音。"""
    try:
        if _show_toast(title, body):
            return True
    except Exception as exc:  # noqa: BLE001
        log.debug("Toast 抛异常：%s", exc)

    _fallback_beep()
    return False


def _format_duration(build: Build) -> str:
    if build.started_at is None or build.finished_at is None:
        return ""
    seconds = int((build.finished_at - build.started_at).total_seconds())
    if seconds < 60:
        return f"{seconds}秒"
    if seconds < 3600:
        return f"{seconds // 60}分{seconds % 60}秒"
    return f"{seconds // 3600}小时{(seconds % 3600) // 60}分"


def notify_build_finished(build_id: int) -> None:
    """构建结束回调。任何异常都在这里被吞掉，绝不影响构建结果。"""
    try:
        with SessionLocal() as db:
            build = db.get(Build, build_id)
            if build is None:
                return

            if not should_notify(db, build.trigger, build.status):
                return

            job = db.get(Job, build.job_id)
            job_name = job.name if job else f"job-{build.job_id}"

            icon = _STATUS_ICON.get(build.status, "•")
            text = _STATUS_TEXT.get(build.status, build.status)
            duration = _format_duration(build)

            title = f"{icon} {job_name} #{build.build_number} {text}"
            body = f"耗时 {duration}" if duration else ""

            notify(title, body)
    except Exception as exc:  # noqa: BLE001
        log.warning("发送通知失败（已忽略）：%s", exc)
```

在 `CI/ci_runner/executor.py` 的 `_after_build` 里已经把签名对齐（调用 `notify_build_finished(build_id, status)`），改成只传 `build_id`：

```python
    def _after_build(self, build_id: int, status: str) -> None:
        """构建结束后的收尾：清理中止信号、发通知。"""
        with self._lock:
            self._abort_events.pop(build_id, None)

        try:
            from .notify import notify_build_finished

            notify_build_finished(build_id)
        except Exception:  # noqa: BLE001  通知失败绝不影响构建结果
            pass
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_notify.py -v
```

预期：8 个测试全部 PASS。

- [ ] **Step 5: 手工验证真实弹窗（非自动化）**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -c "from ci_runner.notify import notify; print(notify('测试通知', '如果你看到这个弹窗，说明 Toast 可用'))"
```

预期：屏幕上出现一条 Windows 通知，命令输出 `True`。若输出 `False` 并听到提示音，说明系统禁用了通知，功能已降级但仍然可用。

- [ ] **Step 6: 跑全量测试并提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/ci_runner/notify.py CI/ci_runner/executor.py CI/tests/test_notify.py && git commit -m "feat(ci): Windows 桌面通知（Toast + 提示音降级）"
```

---

## Task 9: 前端 —— 外壳、任务列表、任务编辑

**Files:**
- Create: `CI/web/index.html`
- Create: `CI/web/style.css`
- Create: `CI/web/app.js`
- Modify: `CI/ci_runner/main.py`（托管静态文件）

**Interfaces:**
- Consumes: 全部 `/api` 接口
- Produces: 浏览器可用的三个页面视图（列表、编辑、历史），并给 Task 10 留出控制台视图的挂载点

- [ ] **Step 1: 让 FastAPI 托管静态文件**

修改 `CI/ci_runner/main.py`，在文件末尾追加：

```python
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


@app.get("/")
def index():
    return FileResponse(config.WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(config.WEB_DIR)), name="static")
```

- [ ] **Step 2: 写页面骨架**

创建 `CI/web/index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>CI Runner</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header id="topbar">
    <div class="brand">🔧 CI Runner</div>
    <nav>
      <a href="#/jobs" data-nav="jobs">任务</a>
      <a href="#/settings" data-nav="settings">设置</a>
    </nav>
    <div id="queue-badge" title="点击查看队列">—</div>
  </header>

  <main id="view"></main>

  <div id="toast-host"></div>

  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: 写样式**

创建 `CI/web/style.css`：

```css
:root {
  --bg: #f6f7f9;
  --panel: #ffffff;
  --border: #dfe3e8;
  --text: #1f2933;
  --muted: #6b7280;
  --brand: #2563eb;
  --green: #16a34a;
  --red: #dc2626;
  --amber: #d97706;
  --grey: #9ca3af;
  --console-bg: #12151b;
  --console-text: #d7dce3;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
}

#topbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 20px;
  height: 52px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand { font-weight: 600; font-size: 16px; }

#topbar nav { display: flex; gap: 4px; flex: 1; }

#topbar nav a {
  padding: 6px 12px;
  border-radius: 6px;
  color: var(--muted);
  text-decoration: none;
}
#topbar nav a:hover { background: var(--bg); }
#topbar nav a.active { background: #e8efff; color: var(--brand); }

#queue-badge {
  font-size: 13px;
  color: var(--muted);
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
}
#queue-badge.busy { color: var(--amber); border-color: var(--amber); }

#view { padding: 20px; max-width: 1280px; margin: 0 auto; }

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.panel-head h2 { margin: 0; font-size: 17px; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 500; font-size: 13px; }
tr:last-child td { border-bottom: none; }

.dot {
  display: inline-block;
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--grey);
}
.dot.success { background: var(--green); }
.dot.failed  { background: var(--red); }
.dot.timeout { background: var(--red); }
.dot.aborted { background: var(--amber); }
.dot.running { background: var(--amber); animation: pulse 1.2s infinite; }
.dot.queued  { background: var(--grey); }

@keyframes pulse { 50% { opacity: 0.3; } }

button {
  font: inherit;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--panel);
  cursor: pointer;
}
button:hover { background: var(--bg); }
button.primary { background: var(--brand); border-color: var(--brand); color: #fff; }
button.primary:hover { filter: brightness(1.1); }
button.danger { color: var(--red); border-color: #f3c2c2; }
button.small { padding: 3px 8px; font-size: 13px; }
button:disabled { opacity: 0.5; cursor: not-allowed; }

.actions { display: flex; gap: 6px; flex-wrap: wrap; }

.field { margin-bottom: 14px; }
.field label { display: block; margin-bottom: 5px; color: var(--muted); font-size: 13px; }
.field input[type=text], .field input[type=number], .field select, .field textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font: inherit;
}
.field .hint { color: var(--muted); font-size: 12px; margin-top: 4px; }
.field .error { color: var(--red); font-size: 12px; margin-top: 4px; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px; }

.step-row {
  display: grid;
  grid-template-columns: 32px 1fr 120px 2fr 90px auto;
  gap: 8px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.step-row .idx { color: var(--muted); text-align: center; }
.step-row input[type=text] { width: 100%; padding: 7px 9px; border: 1px solid var(--border); border-radius: 6px; font: inherit; }
.step-row input[type=checkbox] { justify-self: center; }

/* 控制台 */
.console {
  background: var(--console-bg);
  color: var(--console-text);
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 13px;
  line-height: 1.55;
  padding: 14px 16px;
  border-radius: 8px;
  height: calc(100vh - 260px);
  min-height: 320px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.console .step-block { border-bottom: 1px solid #262b34; padding: 6px 0; }
.console .step-head { cursor: pointer; user-select: none; font-weight: 600; }
.console .step-head.success { color: #4ade80; }
.console .step-head.failed,
.console .step-head.timeout { color: #f87171; }
.console .step-head.running { color: #fbbf24; }
.console .step-head.skipped,
.console .step-head.aborted { color: #8b95a5; }
.console .step-body { padding-left: 14px; }
.console .step-body.collapsed { display: none; }
.console .line-error { color: #f87171; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid var(--border);
}
.badge.success { background: #e7f6ec; color: var(--green); border-color: #b7e2c5; }
.badge.failed, .badge.timeout { background: #fdeaea; color: var(--red); border-color: #f3c2c2; }
.badge.running { background: #fdf3e3; color: var(--amber); border-color: #f0d5a8; }
.badge.queued, .badge.aborted { background: var(--bg); color: var(--muted); }

.console-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.console-head .spacer { flex: 1; }

#toast-host {
  position: fixed;
  right: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 100;
}
.toast {
  background: #1f2933;
  color: #fff;
  padding: 10px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.2);
  max-width: 380px;
}
.toast.error { background: var(--red); }

.empty { color: var(--muted); padding: 24px; text-align: center; }

dialog {
  border: none;
  border-radius: 10px;
  padding: 24px;
  max-width: 420px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.25);
}
dialog::backdrop { background: rgba(0,0,0,0.35); }
```

- [ ] **Step 4: 写前端逻辑**

创建 `CI/web/app.js`：

```javascript
/* CI Runner 前端。原生 JS，无框架、无构建步骤。 */

const $ = (sel) => document.querySelector(sel);

/* ---------- 通用工具 ---------- */

async function api(path, options = {}) {
  const resp = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (resp.status === 204) return null;
  const text = await resp.text();
  const body = text ? JSON.parse(text) : null;
  if (!resp.ok) {
    const detail = body && body.detail ? body.detail : `请求失败（${resp.status}）`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function toast(message, isError = false) {
  const el = document.createElement("div");
  el.className = "toast" + (isError ? " error" : "");
  el.textContent = message;
  $("#toast-host").appendChild(el);
  setTimeout(() => el.remove(), isError ? 6000 : 3000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}

function fmtTime(value) {
  if (!value) return "—";
  const d = new Date(value);
  return d.toLocaleString("zh-CN", { hour12: false });
}

function fmtDuration(start, end) {
  if (!start || !end) return "—";
  const seconds = Math.max(0, Math.round((new Date(end) - new Date(start)) / 1000));
  if (seconds < 60) return `${seconds}秒`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`;
  return `${Math.floor(seconds / 3600)}小时${Math.floor((seconds % 3600) / 60)}分`;
}

const STATUS_TEXT = {
  success: "成功", failed: "失败", running: "运行中",
  queued: "排队中", aborted: "已中止", timeout: "超时",
  pending: "待执行", skipped: "已跳过",
};
const statusText = (s) => STATUS_TEXT[s] || s || "从未构建";

/* ---------- 路由 ---------- */

const routes = [
  [/^#\/jobs$/, viewJobList],
  [/^#\/jobs\/(\d+)\/edit$/, viewJobEdit],
  [/^#\/jobs\/(\d+)\/builds$/, viewJobHistory],
  [/^#\/jobs\/new$/, viewJobEdit],
  [/^#\/builds\/(\d+)$/, viewConsole],
  [/^#\/queue$/, viewQueue],
  [/^#\/settings$/, viewSettings],
];

let cleanup = null;

async function route() {
  if (typeof cleanup === "function") {
    cleanup();
    cleanup = null;
  }
  const hash = location.hash || "#/jobs";
  for (const [pattern, handler] of routes) {
    const match = hash.match(pattern);
    if (match) {
      document.querySelectorAll("#topbar nav a").forEach((a) => {
        a.classList.toggle("active", hash.startsWith(`#/${a.dataset.nav}`));
      });
      try {
        await handler(...match.slice(1));
      } catch (err) {
        $("#view").innerHTML = `<div class="panel"><p class="error">${escapeHtml(err.message)}</p></div>`;
      }
      return;
    }
  }
  location.hash = "#/jobs";
}

window.addEventListener("hashchange", route);

/* ---------- 顶栏队列徽章 ---------- */

async function refreshBadge() {
  try {
    const data = await api("/api/queue");
    const badge = $("#queue-badge");
    badge.textContent = `运行中 ${data.running_count}/${data.max_workers} · 排队 ${data.queued_count}`;
    badge.classList.toggle("busy", data.running_count > 0 || data.queued_count > 0);
  } catch { /* 服务可能正在关闭，忽略 */ }
}

$("#queue-badge").addEventListener("click", () => { location.hash = "#/queue"; });

/* ---------- 视图：任务列表 ---------- */

async function viewJobList() {
  const jobs = await api("/api/jobs");
  const rows = jobs.map((job) => {
    const last = job.last_build;
    const status = last ? last.status : "";
    return `
      <tr>
        <td><span class="dot ${status}"></span></td>
        <td><a href="#/jobs/${job.id}/edit">${escapeHtml(job.name)}</a></td>
        <td>${escapeHtml(job.workdir)}</td>
        <td>${job.cron_expr ? escapeHtml(job.cron_expr) : "—"}</td>
        <td>${last ? "#" + last.build_number : "—"}</td>
        <td>${last ? statusText(last.status) : "—"}</td>
        <td>${last ? fmtDuration(last.started_at, last.finished_at) : "—"}</td>
        <td class="actions">
          <button class="small primary" data-build="${job.id}">构建</button>
          <button class="small" data-history="${job.id}">历史</button>
          <button class="small" data-edit="${job.id}">编辑</button>
          <button class="small danger" data-delete="${job.id}" data-name="${escapeHtml(job.name)}">删除</button>
        </td>
      </tr>`;
  }).join("");

  $("#view").innerHTML = `
    <div class="panel">
      <div class="panel-head">
        <h2>任务</h2>
        <button class="primary" id="new-job">新建任务</button>
      </div>
      ${jobs.length ? `
      <table>
        <thead><tr>
          <th></th><th>名称</th><th>工作目录</th><th>cron</th>
          <th>最近构建</th><th>结果</th><th>耗时</th><th>操作</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>` : `<p class="empty">还没有任务。点击「新建任务」开始。</p>`}
    </div>`;

  $("#new-job").onclick = () => { location.hash = "#/jobs/new"; };

  document.querySelectorAll("[data-build]").forEach((btn) => {
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        const result = await api(`/api/jobs/${btn.dataset.build}/build`, { method: "POST" });
        toast(`已触发构建 #${result.build_number}`);
        location.hash = `#/builds/${result.build_id}`;
      } catch (err) {
        toast(err.message, true);
        btn.disabled = false;
      }
    };
  });

  document.querySelectorAll("[data-history]").forEach((btn) => {
    btn.onclick = () => { location.hash = `#/jobs/${btn.dataset.history}/builds`; };
  });
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.onclick = () => { location.hash = `#/jobs/${btn.dataset.edit}/edit`; };
  });
  document.querySelectorAll("[data-delete]").forEach((btn) => {
    btn.onclick = async () => {
      const name = btn.dataset.name;
      const typed = prompt(`删除任务「${name}」会一并删除它的全部构建历史。\n请输入任务名确认：`);
      if (typed === null) return;
      if (typed !== name) { toast("输入的任务名不匹配，已取消", true); return; }
      try {
        await api(`/api/jobs/${btn.dataset.delete}`, { method: "DELETE" });
        toast("任务已删除");
        route();
      } catch (err) { toast(err.message, true); }
    };
  });
}

/* ---------- 视图：任务编辑 ---------- */

let stepSeq = 0;

function stepRowHtml(step) {
  const id = `step-${stepSeq++}`;
  return `
    <div class="step-row" data-step="${id}">
      <span class="idx"></span>
      <input type="text" class="s-name" placeholder="步骤名称" value="${escapeHtml(step.name || "")}">
      <select class="s-shell">
        <option value="cmd"${step.shell === "powershell" ? "" : " selected"}>cmd</option>
        <option value="powershell"${step.shell === "powershell" ? " selected" : ""}>powershell</option>
      </select>
      <input type="text" class="s-command" placeholder="要执行的命令" value="${escapeHtml(step.command || "")}">
      <label title="勾选后即使这一步失败也继续跑后面的步骤">
        <input type="checkbox" class="s-continue"${step.continue_on_failure ? " checked" : ""}> 失败继续
      </label>
      <span class="actions">
        <button class="small" data-up>↑</button>
        <button class="small" data-down>↓</button>
        <button class="small danger" data-remove>删</button>
      </span>
    </div>`;
}

function renumber() {
  document.querySelectorAll("#steps .step-row").forEach((row, i) => {
    row.querySelector(".idx").textContent = i + 1;
  });
}

async function viewJobEdit(jobId) {
  const isNew = !jobId;
  const job = isNew
    ? { name: "", description: "", workdir: "", cron_expr: "", timeout_seconds: 1800,
        fail_fast: true, enabled: true, steps: [{ name: "", command: "", shell: "cmd" }] }
    : await api(`/api/jobs/${jobId}`);

  $("#view").innerHTML = `
    <div class="panel">
      <div class="panel-head">
        <h2>${isNew ? "新建任务" : `编辑任务：${escapeHtml(job.name)}`}</h2>
        <button id="back">返回</button>
      </div>

      <div class="grid-2">
        <div class="field">
          <label>任务名称 *</label>
          <input type="text" id="f-name" value="${escapeHtml(job.name)}">
        </div>
        <div class="field">
          <label>工作目录 *（步骤都在这个目录里执行）</label>
          <input type="text" id="f-workdir" value="${escapeHtml(job.workdir)}" placeholder="D:\\work\\myproject">
          <div class="hint" id="workdir-hint"></div>
        </div>
      </div>

      <div class="field">
        <label>描述</label>
        <input type="text" id="f-description" value="${escapeHtml(job.description || "")}">
      </div>

      <div class="grid-2">
        <div class="field">
          <label>cron 表达式（留空表示不启用定时）</label>
          <input type="text" id="f-cron" value="${escapeHtml(job.cron_expr || "")}" placeholder="0 9 * * 1-5">
          <div class="hint" id="cron-hint">例：0 9 * * 1-5 表示工作日 9 点</div>
        </div>
        <div class="field">
          <label>单步骤超时（秒，60–86400）</label>
          <input type="number" id="f-timeout" value="${job.timeout_seconds}" min="60" max="86400">
        </div>
      </div>

      <div class="grid-2">
        <div class="field">
          <label><input type="checkbox" id="f-failfast"${job.fail_fast ? " checked" : ""}> 步骤失败即停止后续步骤</label>
        </div>
        <div class="field">
          <label><input type="checkbox" id="f-enabled"${job.enabled ? " checked" : ""}> 启用定时触发</label>
        </div>
      </div>

      <div class="panel-head" style="margin-top:24px">
        <h2>步骤</h2>
        <button id="add-step">添加步骤</button>
      </div>
      <div id="steps">${job.steps.map(stepRowHtml).join("")}</div>
      <div class="hint" style="margin-top:8px">步骤按从上到下的顺序执行，用 ↑ ↓ 调整顺序。</div>

      <div class="panel-head" style="margin-top:24px">
        <span></span>
        <span class="actions">
          <button id="cancel">取消</button>
          <button class="primary" id="save">保存</button>
        </span>
      </div>
    </div>`;

  renumber();

  $("#back").onclick = $("#cancel").onclick = () => { location.hash = "#/jobs"; };

  $("#add-step").onclick = () => {
    $("#steps").insertAdjacentHTML("beforeend", stepRowHtml({ name: "", command: "", shell: "cmd" }));
    renumber();
  };

  $("#steps").addEventListener("click", (event) => {
    const row = event.target.closest(".step-row");
    if (!row) return;
    if (event.target.matches("[data-remove]")) {
      if (document.querySelectorAll("#steps .step-row").length === 1) {
        toast("至少需要一个步骤", true);
        return;
      }
      row.remove();
      renumber();
    } else if (event.target.matches("[data-up]")) {
      const prev = row.previousElementSibling;
      if (prev) { row.parentNode.insertBefore(row, prev); renumber(); }
    } else if (event.target.matches("[data-down]")) {
      const next = row.nextElementSibling;
      if (next) { row.parentNode.insertBefore(next, row); renumber(); }
    }
  });

  // cron 即时校验：失焦时问一次后端，把下次触发时间显示出来
  const cronInput = $("#f-cron");
  cronInput.addEventListener("blur", async () => {
    const hint = $("#cron-hint");
    const expr = cronInput.value.trim();
    if (!expr) {
      hint.textContent = "例：0 9 * * 1-5 表示工作日 9 点";
      hint.style.color = "";
      return;
    }
    try {
      const result = await api("/api/jobs/validate-cron", {
        method: "POST",
        body: JSON.stringify({ cron_expr: expr }),
      });
      hint.textContent = "下次触发：" + result.next_runs.map(fmtTime).join("、");
      hint.style.color = "var(--green)";
    } catch (err) {
      hint.textContent = err.message;
      hint.style.color = "var(--red)";
    }
  });

  $("#save").onclick = async () => {
    const steps = [...document.querySelectorAll("#steps .step-row")].map((row) => ({
      name: row.querySelector(".s-name").value.trim(),
      command: row.querySelector(".s-command").value.trim(),
      shell: row.querySelector(".s-shell").value,
      continue_on_failure: row.querySelector(".s-continue").checked,
    }));

    const payload = {
      name: $("#f-name").value.trim(),
      description: $("#f-description").value.trim(),
      workdir: $("#f-workdir").value.trim(),
      cron_expr: cronInput.value.trim() || null,
      timeout_seconds: Number($("#f-timeout").value),
      fail_fast: $("#f-failfast").checked,
      enabled: $("#f-enabled").checked,
      steps,
    };

    try {
      if (isNew) {
        await api("/api/jobs", { method: "POST", body: JSON.stringify(payload) });
      } else {
        await api(`/api/jobs/${jobId}`, { method: "PUT", body: JSON.stringify(payload) });
      }
      toast("已保存");
      location.hash = "#/jobs";
    } catch (err) {
      toast(err.message, true);
    }
  };
}

/* ---------- 视图：构建历史 ---------- */

async function viewJobHistory(jobId) {
  const [job, builds] = await Promise.all([
    api(`/api/jobs/${jobId}`),
    api(`/api/jobs/${jobId}/builds`),
  ]);

  const rows = builds.map((b) => `
    <tr>
      <td><span class="dot ${b.status}"></span></td>
      <td><a href="#/builds/${b.id}">#${b.build_number}</a></td>
      <td>${statusText(b.status)}</td>
      <td>${b.trigger === "cron" ? "定时" : "手动"}</td>
      <td>${fmtTime(b.started_at)}</td>
      <td>${fmtDuration(b.started_at, b.finished_at)}</td>
    </tr>`).join("");

  $("#view").innerHTML = `
    <div class="panel">
      <div class="panel-head">
        <h2>构建历史：${escapeHtml(job.name)}</h2>
        <button id="back">返回任务列表</button>
      </div>
      ${builds.length ? `
      <table>
        <thead><tr><th></th><th>构建号</th><th>结果</th><th>触发</th><th>开始时间</th><th>耗时</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>` : `<p class="empty">还没有构建记录。</p>`}
    </div>`;

  $("#back").onclick = () => { location.hash = "#/jobs"; };
}

/* ---------- 视图：队列 ---------- */

async function viewQueue() {
  const data = await api("/api/queue");
  const render = (list) => list.length
    ? list.map((b) => `<tr>
        <td><a href="#/builds/${b.id}">${escapeHtml(b.job_name)} #${b.build_number}</a></td>
        <td>${statusText(b.status)}</td>
        <td>${b.trigger === "cron" ? "定时" : "手动"}</td>
      </tr>`).join("")
    : `<tr><td colspan="3" class="empty">空</td></tr>`;

  $("#view").innerHTML = `
    <div class="panel">
      <div class="panel-head"><h2>运行中（并发上限 ${data.max_workers}）</h2></div>
      <table><tbody>${render(data.running)}</tbody></table>
    </div>
    <div class="panel">
      <div class="panel-head"><h2>排队中</h2></div>
      <table><tbody>${render(data.queued)}</tbody></table>
    </div>`;
}

/* ---------- 视图：设置 ---------- */

async function viewSettings() {
  const s = await api("/api/settings");
  $("#view").innerHTML = `
    <div class="panel">
      <div class="panel-head"><h2>设置</h2></div>
      <div class="field">
        <label>并发构建数（1–16，同一任务始终串行）</label>
        <input type="number" id="s-workers" value="${s.max_workers}" min="1" max="16">
      </div>
      <div class="field">
        <label><input type="checkbox" id="s-fail"${s.notify_on_failure === "1" ? " checked" : ""}> 构建失败/超时/中止时通知</label>
      </div>
      <div class="field">
        <label><input type="checkbox" id="s-manual"${s.notify_on_success_manual === "1" ? " checked" : ""}> 手动触发的构建成功时通知</label>
      </div>
      <div class="field">
        <label><input type="checkbox" id="s-cron"${s.notify_on_success_cron === "1" ? " checked" : ""}> 定时触发的构建成功时通知</label>
      </div>
      <button class="primary" id="save-settings">保存</button>
    </div>`;

  $("#save-settings").onclick = async () => {
    try {
      await api("/api/settings", {
        method: "PUT",
        body: JSON.stringify({
          max_workers: $("#s-workers").value,
          notify_on_failure: $("#s-fail").checked ? "1" : "0",
          notify_on_success_manual: $("#s-manual").checked ? "1" : "0",
          notify_on_success_cron: $("#s-cron").checked ? "1" : "0",
        }),
      });
      toast("设置已保存");
      refreshBadge();
    } catch (err) { toast(err.message, true); }
  };
}

/* ---------- 视图：控制台（Task 10 实现完整版，这里先占位） ---------- */

async function viewConsole(buildId) {
  $("#view").innerHTML = `<div class="panel"><h2>构建 #${buildId}</h2>
    <pre class="console" id="console">加载中…</pre></div>`;
}

/* ---------- 启动 ---------- */

setInterval(refreshBadge, 3000);
refreshBadge();
route();
```

- [ ] **Step 5: 手工验证**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m uvicorn ci_runner.main:app --host 127.0.0.1 --port 8899
```

浏览器打开 `http://127.0.0.1:8899`，确认：
1. 任务列表能显示（初次为空，有"还没有任务"提示）
2. 点「新建任务」能进编辑页，工作目录填 `D:\develop\claudecode-workspace\claude_5\CI`，加一个 `echo 你好` 步骤，保存成功
3. cron 输入 `*/5 * * * *` 后失焦，下方出现 5 个下次触发时间
4. 顶栏队列徽章每 3 秒刷新
5. 点「构建」会跳到 `#/builds/N`，控制台暂时只显示"加载中…"（Task 10 实现）

- [ ] **Step 6: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/web CI/ci_runner/main.py && git commit -m "feat(ci): 前端外壳、任务列表与任务编辑页"
```

---

## Task 10: 前端 —— 控制台与实时日志

**Files:**
- Modify: `CI/web/app.js`（替换 `viewConsole` 占位实现）

**Interfaces:**
- Consumes: `GET /api/builds/{id}`、`GET /api/builds/{id}/log`、`GET /api/builds/{id}/stream`、`POST /api/builds/{id}/abort`
- Produces: 完整的控制台视图，并注册 `cleanup` 让路由切换时关闭 SSE 连接

- [ ] **Step 1: 替换 viewConsole 实现**

在 `CI/web/app.js` 中，把 `/* ---------- 视图：控制台（Task 10 实现完整版，这里先占位） ---------- */` 那一段整体替换为：

```javascript
/* ---------- 视图：控制台 ---------- */

const TERMINAL_STATUSES = ["success", "failed", "aborted", "timeout"];

async function viewConsole(buildId) {
  const build = await api(`/api/builds/${buildId}`);

  $("#view").innerHTML = `
    <div class="panel">
      <div class="console-head">
        <a href="#/jobs/${build.job_id}/builds">← 返回历史</a>
        <h2 style="margin:0">${escapeHtml(build.job_name)} #${build.build_number}</h2>
        <span class="badge ${build.status}" id="c-status">${statusText(build.status)}</span>
        <span id="c-timer" class="hint"></span>
        <span class="hint">${build.trigger === "cron" ? "定时触发" : "手动触发"}</span>
        <span class="spacer"></span>
        <label class="hint"><input type="checkbox" id="c-autoscroll" checked> 自动滚动</label>
        <a href="/api/builds/${buildId}/download"><button class="small">下载日志</button></a>
        <button class="small danger" id="c-abort">中止</button>
      </div>
      ${build.error_message ? `<p class="error" style="color:var(--red)">${escapeHtml(build.error_message)}</p>` : ""}
      <div class="console" id="console"></div>
    </div>`;

  const consoleEl = $("#console");
  const statusEl = $("#c-status");
  const timerEl = $("#c-timer");
  const abortBtn = $("#c-abort");
  const autoscroll = $("#c-autoscroll");

  let currentStepBlock = null;
  let currentStepBody = null;
  let stepBlocks = new Map();
  let finished = TERMINAL_STATUSES.includes(build.status);
  let startedAt = build.started_at ? new Date(build.started_at) : null;
  let statusPoll = null;
  let source = null;

  abortBtn.disabled = finished;
  if (finished) abortBtn.textContent = "已结束";

  /* --- 已结束的构建：先按步骤结果铺好折叠块，再把日志填进去 --- */
  function buildStepBlocks(stepResults) {
    stepBlocks.clear();
    stepResults.forEach((step, index) => {
      const block = document.createElement("div");
      block.className = "step-block";
      const head = document.createElement("div");
      head.className = `step-head ${step.status}`;
      head.textContent = stepHeadText(step, index, stepResults.length);
      const body = document.createElement("div");
      body.className = "step-body";
      head.onclick = () => body.classList.toggle("collapsed");
      block.appendChild(head);
      block.appendChild(body);
      consoleEl.appendChild(block);
      stepBlocks.set(step.order_index, { head, body, status: step.status });
    });
  }

  function stepHeadText(step, index, total) {
    const duration = fmtDuration(step.started_at, step.finished_at);
    const suffix = duration === "—" ? "" : `  ${duration}`;
    return `[${index + 1}/${total}] ${step.name}  ${statusText(step.status)}${suffix}`;
  }

  /* --- 日志落位：根据分隔头判断当前属于哪一步 --- */
  const STEP_HEADER = /^────── \[(\d+)\/(\d+)\] (.*) ──────$/;

  function appendLine(text) {
    const match = text.match(STEP_HEADER);
    if (match) {
      const index = Number(match[1]) - 1;
      const entry = stepBlocks.get(index);
      if (entry) {
        // 新的一步开始：把上一步的块折叠，展开当前块
        if (currentStepBlock) currentStepBlock.body.classList.add("collapsed");
        entry.body.classList.remove("collapsed");
        currentStepBlock = entry;
        currentStepBody = entry.body;
      } else {
        currentStepBody = consoleEl;
      }
      currentStepBody.appendChild(document.createTextNode(text + "\n"));
      return;
    }

    const target = currentStepBody || consoleEl;
    const line = document.createElement("div");
    line.textContent = text;
    if (text.startsWith("[error]") || text.startsWith("[timeout]")) {
      line.className = "line-error";
    }
    target.appendChild(line);
  }

  function autoscrollToBottom() {
    if (autoscroll.checked) consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  function updateStepStatuses(stepResults) {
    stepResults.forEach((step, index) => {
      const entry = stepBlocks.get(step.order_index);
      if (!entry) return;
      entry.head.className = `step-head ${step.status}`;
      entry.head.textContent = stepHeadText(step, index, stepResults.length);
    });
  }

  async function refreshBuild() {
    try {
      const fresh = await api(`/api/builds/${buildId}`);
      statusEl.className = `badge ${fresh.status}`;
      statusEl.textContent = statusText(fresh.status);
      updateStepStatuses(fresh.steps);
      if (fresh.started_at) startedAt = new Date(fresh.started_at);
      if (TERMINAL_STATUSES.includes(fresh.status) && !finished) {
        finished = true;
        abortBtn.disabled = true;
        abortBtn.textContent = "已结束";
        if (statusPoll) clearInterval(statusPoll);
      }
    } catch { /* 忽略瞬时失败 */ }
  }

  /* --- 首次加载：先铺步骤块，再拉全量日志 --- */
  buildStepBlocks(build.steps);
  if (build.steps.length > 0) {
    const running = build.steps.find((s) => s.status === "running") || build.steps[0];
    const entry = stepBlocks.get(running.order_index);
    if (entry) { entry.body.classList.remove("collapsed"); currentStepBlock = entry; currentStepBody = entry.body; }
  }

  let offset = 0;
  const initial = await api(`/api/builds/${buildId}/log?offset=0`);
  initial.lines.forEach(appendLine);
  offset = initial.next_offset;
  autoscrollToBottom();

  /* --- 已结束：不再连 SSE --- */
  if (finished) {
    timerEl.textContent = `耗时 ${fmtDuration(build.started_at, build.finished_at)}`;
    return;
  }

  /* --- 运行中：SSE 实时推送 --- */
  source = new EventSource(`/api/builds/${buildId}/stream?offset=${offset}`);
  cleanup = () => { if (source) source.close(); if (statusPoll) clearInterval(statusPoll); };

  source.addEventListener("log", (event) => {
    appendLine(JSON.parse(event.data));
    autoscrollToBottom();
  });

  source.addEventListener("status", (event) => {
    const data = JSON.parse(event.data);
    statusEl.className = `badge ${data.status}`;
    statusEl.textContent = statusText(data.status);
  });

  source.addEventListener("truncated", () => {
    consoleEl.appendChild(Object.assign(document.createElement("div"), {
      className: "line-error",
      textContent: "（日志过快，部分早期输出已从内存中滚出，完整内容见下载的日志文件）",
    }));
  });

  source.addEventListener("end", async () => {
    source.close();
    source = null;
    finished = true;
    abortBtn.disabled = true;
    abortBtn.textContent = "已结束";
    // 收尾：把最后一段日志和每步状态补齐
    const tail = await api(`/api/builds/${buildId}/log?offset=${offset}`);
    tail.lines.forEach(appendLine);
    offset = tail.next_offset;
    await refreshBuild();
    const finalBuild = await api(`/api/builds/${buildId}`);
    timerEl.textContent = `耗时 ${fmtDuration(finalBuild.started_at, finalBuild.finished_at)}`;
    autoscrollToBottom();
  });

  source.onerror = () => {
    // SSE 断了（服务重启等）：退回轮询，保证还能看到结果
    if (source) { source.close(); source = null; }
    if (!statusPoll) statusPoll = setInterval(refreshBuild, 2000);
  };

  /* --- 计时器 --- */
  const tick = () => {
    if (finished || !startedAt) { return; }
    const seconds = Math.round((Date.now() - startedAt) / 1000);
    timerEl.textContent = `已运行 ${seconds < 60 ? seconds + "秒" : Math.floor(seconds / 60) + "分" + (seconds % 60) + "秒"}`;
  };
  tick();
  const timerHandle = setInterval(tick, 1000);

  /* --- 中止 --- */
  abortBtn.onclick = async () => {
    if (!confirm("确定要中止这次构建吗？正在执行的命令会被强制结束。")) return;
    abortBtn.disabled = true;
    try {
      await api(`/api/builds/${buildId}/abort`, { method: "POST" });
      toast("已请求中止");
      refreshBuild();
    } catch (err) {
      toast(err.message, true);
      abortBtn.disabled = false;
    }
  };

  const previousCleanup = cleanup;
  cleanup = () => {
    if (previousCleanup) previousCleanup();
    clearInterval(timerHandle);
    if (source) source.close();
    if (statusPoll) clearInterval(statusPoll);
  };
}
```

- [ ] **Step 2: 手工验证**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m uvicorn ci_runner.main:app --host 127.0.0.1 --port 8899
```

浏览器验证：
1. 建一个两步任务（`echo 第一步内容` / `echo 第二步内容`），点构建
2. 控制台能看到两个步骤块，日志实时逐行出现
3. 第一步的块在第二步开始时自动折叠
4. 顶部状态徽章从"排队中"变"运行中"再变"成功"，计时器在跑
5. 建一个含 `timeout /t 60 >nul` 的任务，运行中点「中止」，状态变「已中止」
6. 切换页面再回来，SSE 连接被正确关闭（浏览器 Network 面板里没有残留的 eventsource 请求）

- [ ] **Step 3: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI/web/app.js && git commit -m "feat(ci): 控制台实时日志（SSE）与中止操作"
```

---

## Task 11: 启动脚本、README 与端到端冒烟

**Files:**
- Create: `CI/start.bat`
- Create: `CI/README.md`
- Create: `CI/tests/test_end_to_end.py`

**Interfaces:**
- Consumes: 全部已完成功能
- Produces: 可交付的工具

- [ ] **Step 1: 写启动脚本**

创建 `CI/start.bat`：

```bat
@echo off
chcp 65001 > nul
setlocal

rem 切到脚本所在目录，这样双击也能找到相对路径
cd /d "%~dp0"

set HOST=127.0.0.1
set PORT=8899
set URL=http://%HOST%:%PORT%

echo ============================================
echo   CI Runner
echo   启动中... 界面地址 %URL%
echo   按 Ctrl+C 停止
echo ============================================
echo.

rem 先检查端口有没有被占用
netstat -ano | findstr ":%PORT%" | findstr "LISTENING" > nul
if not errorlevel 1 (
    echo [错误] 端口 %PORT% 已被占用。
    echo        请关掉占用该端口的程序，或修改 ci_runner\config.py 里的 PORT。
    pause
    exit /b 1
)

rem 后台等端口就绪后开浏览器
start "" /b cmd /c "for /l %%i in (1,1,30) do (timeout /t 1 /nobreak >nul & powershell -NoProfile -Command \"try{ $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%/api/health'; if($r.StatusCode -eq 200){ Start-Process '%URL%'; exit } }catch{}; exit\" & exit)"

python -m uvicorn ci_runner.main:app --host %HOST% --port %PORT%

echo.
echo 服务已停止。
pause
```

- [ ] **Step 2: 写 README**

创建 `CI/README.md`：

```markdown
# CI Runner — 本机轻量 CI 工具

在一台不能安装 Jenkins 的电脑上，提供 Jenkins 的核心子集：多任务、网页配置步骤、
手动/cron 触发、实时构建日志、构建历史、完成通知。

**不注册系统服务、不需要管理员权限、不联网、不需要新增任何 Python 包。**

## 快速开始

双击 `start.bat`，浏览器会自动打开 `http://127.0.0.1:8899`。

停止：在启动窗口按 `Ctrl+C`。

## 核心概念

- **任务（Job）**：绑定一个**已存在的本地目录**，加一串**步骤**。工具不拉代码。
- **步骤（Step）**：一条命令，用 `cmd` 或 `powershell` 执行。按顺序跑。
- **构建（Build）**：任务的一次执行，有独立编号和完整日志。

## 常用操作

| 想做的事 | 怎么做 |
|---|---|
| 立即跑一次 | 任务列表点「构建」 |
| 每天定时跑 | 编辑任务，填 cron 表达式，如 `0 9 * * 1-5` |
| 看实时输出 | 点构建号进控制台 |
| 某步失败也要继续 | 编辑任务，勾掉「失败即停」，或给那一步勾「失败继续」 |
| 改并发数 | 设置页，1–16 |
| 找历史日志 | 任务列表点「历史」，或直接看 `logs/<任务ID>/<构建号>.log` |

## 行为约定

- **同一任务不并发**：已在跑时再次触发会被拒绝（提示"已有构建在排队"）
- **不同任务可并行**：数量受设置里的并发数限制
- **定时触发遇到忙**：跳过本次（不排队），避免任务积压失控
- **删除任务**：有构建在跑时会被拒绝，需先中止
- **通知**：失败/超时/中止必通知；手动触发的成功通知；定时触发的成功默认不通知

## 目录说明

```
ci_runner/    后端代码
web/          前端页面（纯静态，无构建步骤）
data/         SQLite 数据库（运行时生成）
logs/         构建日志，按 任务ID/构建号.log 存放
tests/        测试
```

## 开发

```bash
python -m pytest -v          # 跑全部测试
```

## 常见问题

**端口 8899 被占用？**
改 `ci_runner/config.py` 里的 `PORT`，同时改 `start.bat` 里的 `PORT`。

**日志里中文是问号？**
说明某个被调用的程序没走 UTF-8 输出。工具已强制 `chcp 65001` 和
`PYTHONIOENCODING=utf-8`，若仍乱码，请检查该程序自身的编码设置。

**没有桌面通知？**
系统可能禁用了通知。工具会自动降级为提示音。检查
「设置 → 系统 → 通知」里 "CI Runner" 是否被允许。

**想在另一台机器上用？**
整个 `CI` 目录拷过去（可删掉 `data/` 和 `logs/`），装好 Python 3.11
和那几个已列出的包即可。
```

- [ ] **Step 3: 写端到端冒烟测试**

创建 `CI/tests/test_end_to_end.py`：

```python
"""端到端冒烟：建任务 → 触发 → 等结束 → 断言状态、日志、步骤。"""

import time

import pytest

from ci_runner.db import SessionLocal
from ci_runner.executor import Executor
from ci_runner.main import app


@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient

    ex = Executor(session_factory=SessionLocal)
    ex.start()
    app.state.executor = ex
    with TestClient(app) as c:
        yield c
    ex.shutdown()


def test_full_flow_success_then_failure(api_client, tmp_path):
    """一个任务跑成功；另一个故意失败并跳过后续步骤。"""

    ok_job = api_client.post("/api/jobs", json={
        "name": "e2e-成功",
        "description": "",
        "workdir": str(tmp_path),
        "cron_expr": None,
        "timeout_seconds": 120,
        "fail_fast": True,
        "enabled": True,
        "steps": [
            {"name": "打招呼", "command": "echo 你好世界", "shell": "cmd"},
            {"name": "列目录", "command": "dir /b", "shell": "cmd"},
        ],
    }).json()
    assert "id" in ok_job

    build_id = api_client.post(f"/api/jobs/{ok_job['id']}/build").json()["build_id"]

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        detail = api_client.get(f"/api/builds/{build_id}").json()
        if detail["status"] not in ("queued", "running"):
            break
        time.sleep(0.1)

    assert detail["status"] == "success"
    assert [s["status"] for s in detail["steps"]] == ["success", "success"]

    log = api_client.get(f"/api/builds/{build_id}/log?offset=0").json()
    text = "\n".join(log["lines"])
    assert "你好世界" in text
    assert "#1" in text

    bad_job = api_client.post("/api/jobs", json={
        "name": "e2e-失败",
        "description": "",
        "workdir": str(tmp_path),
        "cron_expr": None,
        "timeout_seconds": 120,
        "fail_fast": True,
        "enabled": True,
        "steps": [
            {"name": "先成功", "command": "echo ok", "shell": "cmd"},
            {"name": "故意失败", "command": "exit 7", "shell": "cmd"},
            {"name": "不该跑到", "command": "echo nope", "shell": "cmd"},
        ],
    }).json()

    bad_build = api_client.post(f"/api/jobs/{bad_job['id']}/build").json()["build_id"]

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        detail2 = api_client.get(f"/api/builds/{bad_build}").json()
        if detail2["status"] not in ("queued", "running"):
            break
        time.sleep(0.1)

    assert detail2["status"] == "failed"
    assert [s["status"] for s in detail2["steps"]] == ["success", "failed", "skipped"]
    assert detail2["exit_code"] == 7

    # 步骤名被冗余存进历史，步骤改名不影响旧记录
    assert [s["name"] for s in detail2["steps"]] == ["先成功", "故意失败", "不该跑到"]


def test_health_and_static_page_served(api_client):
    assert api_client.get("/api/health").json()["status"] == "ok"

    page = api_client.get("/")
    assert page.status_code == 200
    assert "CI Runner" in page.text

    css = api_client.get("/static/style.css")
    assert css.status_code == 200
```

- [ ] **Step 4: 运行端到端测试**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest tests/test_end_to_end.py -v
```

预期：2 个测试 PASS。

- [ ] **Step 5: 跑全量测试**

```bash
cd "D:/develop/claudecode-workspace/claude_5/CI" && python -m pytest -v
```

预期：全部 PASS（约 60 个测试）。

- [ ] **Step 6: 双击 start.bat 做一次真实冒烟**

关掉所有 uvicorn 进程，双击 `CI/start.bat`。确认：

1. 窗口出现启动横幅，没有端口占用报错
2. 浏览器自动打开 `http://127.0.0.1:8899`
3. 建一个真实任务：工作目录填一个真实的前端项目（如
   `D:\develop\claudecode-workspace\claude_5\sliding-puzzle`），步骤填 `npm run build`
4. 点构建，控制台能看到 npm 的真实输出且**中文不乱码**
5. 构建结束后收到 Windows 桌面通知
6. 在启动窗口按 `Ctrl+C`，服务停止

- [ ] **Step 7: 提交**

```bash
cd "D:/develop/claudecode-workspace/claude_5" && git add CI && git commit -m "feat(ci): 启动脚本、README 与端到端冒烟测试"
```

---

## 完成标准

全部 11 个任务完成后，应满足：

- [ ] `python -m pytest -v` 全绿
- [ ] 双击 `CI/start.bat` 能起来并自动开浏览器
- [ ] 能新建任务、手动构建、看到实时日志
- [ ] 能配 cron 并到点自动构建
- [ ] 构建结束能收到桌面通知
- [ ] 中文日志不乱码
- [ ] 超时和中止能真正杀掉进程树（没有残留进程）
- [ ] 全程没有安装任何新的 pip 包
