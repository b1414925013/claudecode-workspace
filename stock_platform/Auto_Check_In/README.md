# 夸克网盘自动签到

通过 **GitHub Actions** 每日自动执行，实现夸克网盘的自动签到，并支持企业微信机器人推送通知。

> 源代码参考自 [BNDou/Auto_Check_In](https://github.com/BNDou/Auto_Check_In)，在此基础上进行了优化重构。

---

## 功能特性

- ✅ 自动签到，领取每日空间奖励
- ✅ 支持多账号同时签到
- ✅ 连签进度统计
- ✅ 企业微信机器人实时推送
- ✅ GitHub Actions 自动执行

---

## 快速开始

### 1. 获取企业微信机器人 WebHook

1. 打开 [企业微信](https://work.weixin.qq.com/)，注册一个企业
2. 在【我的企业】→【微信插件】，用微信扫码邀请关注
3. 在企业群中添加机器人，获取 **WebHook** 地址

> ⚠️ WebHook 不要泄露给他人

### 2. 获取 COOKIE_QUARK

#### 抓包步骤（手机端）

1. 手机安装抓包工具（如 Stream、Thor）
2. 打开抓包，访问夸克抽奖页
3. 找到 `https://drive-m.quark.cn/1/clouddrive/capacity/growth/info` 请求
4. 从 URL 中提取 `kps`、`sign`、`vcode` 三个参数

#### 参数格式

```
user=张三;kps=xxx;sign=xxx;vcode=xxx
```

- `user` 为自定义名称，用于多账号区分
- 多账户用 `&&` 或换行分隔

```
user=账号1;kps=xxx;sign=xxx;vcode=xxx&&user=账号2;kps=xxx;sign=xxx;vcode=xxx
```

### 3. 部署到 GitHub

1. **Fork** 本仓库到你的 GitHub 账号
2. 进入 **Settings → Secrets and variables → Actions**
3. 添加两个 Secret：
   - `COOKIE_QUARK` - 填入签到参数
   - `WEBHOOK`（或 `WebHook`）- 企业微信 WebHook 地址（可选）

### 4. 触发签到

- **自动执行**：每天北京时间 08:00 自动运行
- **手动触发**：进入 Actions → Quark → Run workflow

---

## 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `COOKIE_QUARK` | ✅ | 签到参数，多账户用 `&&` 或换行分隔 |
| `WEBHOOK` / `WebHook` | ❌ | 企业微信机器人 WebHook，用于推送通知 |

---

## API 接口说明

### 获取签到信息

```
GET https://drive-m.quark.cn/1/clouddrive/capacity/growth/info
```

### 执行签到

```
POST https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign
```

请求体：
```json
{"sign_cyclic": true}
```

### 查询抽奖余额（可选）

```
GET https://coral2.quark.cn/currency/v1/queryBalance
```

---

## 本地运行

```bash
# 设置环境变量
export COOKIE_QUARK="user=张三;kps=xxx;sign=xxx;vcode=xxx"
export WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

# 运行
python Sign_In.py
```

---

## License

MIT