# nGQL vs openCypher 9

| 差异项 | nGQL | openCypher 9 |
|-------|------|--------------|
| Schema | 强 Schema | 弱 Schema |
| 相等运算 | == | = |
| 幂运算 | pow(x,y) | ^ |
| 边 Rank | 支持 | 不支持 |
| 事务 | 无 | 有 |
| GO 语句 | 原生支持 | 不支持 |
| 管道符 | 支持 | 不支持 |

---

## 客户端连接

### Nebula Console

```bash
# 连接
nebula-console -addr 192.168.1.100 -port 9669 -u root -p password

# 常用命令
SHOW SPACES;
USE <space_name>;
SHOW TAGS;
SHOW EDGES;
```