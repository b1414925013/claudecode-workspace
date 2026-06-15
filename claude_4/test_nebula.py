# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
import time

pool = ConnectionPool()
pool.init([("localhost", 9669)], Config())
session = pool.get_session("root", "nebula")

def ok(r, msg=""):
    if not r.is_succeeded():
        print(f"  [FAIL] {r.error_msg()}")
        return False
    if msg:
        print(f"  [OK] {msg}")
    return True

def wait_insert(ngql, max_wait=30, desc=""):
    schema_errors = ["No schema found", "Tag not found", "EdgeNotFound", "TagNotFound", "Edge not found"]
    for i in range(max_wait):
        r = session.execute(ngql)
        if r.is_succeeded():
            if desc:
                print(f"  [OK] {desc}")
            return True
        err = r.error_msg()
        if any(e in err for e in schema_errors):
            if i % 5 == 0 or i < 3:
                print(f"  等待 schema 同步中 ({i}s)... 错误: {err.strip('.')}")
            time.sleep(1)
            continue
        print(f"  [FAIL] {err}")
        return False
    print(f"  [FAIL] schema 在 {max_wait}s 内未就绪")
    return False

def show(r):
    if not r.is_succeeded():
        print(f"  [FAIL] {r.error_msg()}")
        return
    print(f"  列: {r.keys()}")
    for row in r.rows():
        # .value 返回 Python 原生类型（bytes/int/float/bool）
        vals = [v.value.decode() if isinstance(v.value, bytes) else v.value for v in row.values]
        print(f"  行: {vals}")

# ===== 1. 准备图空间 =====
print(">>> 1. 准备图空间")
ok(session.execute(
    'CREATE SPACE IF NOT EXISTS my_graph '
    '(partition_num=1, replica_factor=1, vid_type=FIXED_STRING(32));'
), "空间已就绪")
session.execute("USE my_graph;")

# ===== 2. 定义 Schema =====
print("\n>>> 2. 定义 Schema")
session.execute("CREATE TAG IF NOT EXISTS person(name string, age int);")
session.execute("CREATE EDGE IF NOT EXISTS follow(degree int);")

# ===== 3. 插入数据（带重试，等待 schema 同步）=====
print("\n>>> 3. 插入数据")
wait_insert(
    'INSERT VERTEX person(name, age) VALUES '
    '"p1":("Alice", 30), "p2":("Bob", 25);',
    desc="顶点数据已插入"
)
wait_insert(
    'INSERT EDGE follow(degree) VALUES "p1"->"p2":(85);',
    desc="边数据已插入"
)

# ===== 4. FETCH PROP 查询 =====
print("\n>>> 4. FETCH PROP 查询")
r = session.execute('FETCH PROP ON person "p1" YIELD person.name, person.age;')
show(r)

# ===== 5. 索引 & MATCH 查询 =====
print("\n>>> 5. 创建索引 & MATCH 查询")
session.execute("CREATE TAG INDEX IF NOT EXISTS person_age_index ON person(age);")
session.execute("REBUILD TAG INDEX person_age_index;")

# 等待索引就绪
for i in range(15):
    r = session.execute("SHOW TAG INDEXES;")
    if r.is_succeeded():
        rows = list(r.rows())
        if rows and "person_age_index" in str(rows[0].values[0].value):
            break
    time.sleep(1)

r = session.execute(
    'USE my_graph; '
    'MATCH (v:person) WHERE v.person.age > 20 '
    'RETURN v.person.name AS name, v.person.age AS age;'
)
show(r)

session.release()
pool.close()
print("\n=== 全部完成 ===")
