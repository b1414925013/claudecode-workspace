"""Seed test data for development."""
import asyncio
from tortoise import Tortoise
from ksm_core.database import init_db, close_db
from ksm_core.models import User, Environment, DBCredential, ToolboxLink, EnvPermission, SecretCache
from ksm_core.security import hash_password
from ksm_core.crypto_utils import aes_encrypt


async def main():
    print("Connecting to database...")
    await init_db()
    from tortoise import Tortoise as T
    await T.generate_schemas()

    # ── Users ──
    users_data = [
        ("admin",     hash_password("admin123"), "系统管理员",   "admin@ksm.local",    "admin",     True),
        ("dev-zhang", hash_password("dev123"),   "张开发",       "zhang@ksm.local",     "developer", True),
        ("dev-li",    hash_password("dev123"),   "李测试",       "li@ksm.local",        "developer", True),
        ("ops-wang",  hash_password("ops123"),   "王运维",       "wang@ksm.local",      "ops",       True),
        ("auditor",   hash_password("audit123"), "审计员",       "audit@ksm.local",     "auditor",   True),
    ]
    created_users = []
    for username, pw_hash, nickname, email, role, active in users_data:
        user, _ = await User.get_or_create(
            username=username,
            defaults=dict(password_hash=pw_hash, nickname=nickname, email=email, role=role, is_active=active),
        )
        created_users.append(user)
        print(f"  User {'created' if _ else 'exists'}: {username} ({role})")

    admin = created_users[0]

    # ── Environments ──
    envs_data = [
        ("dev",       "开发环境",        "https://api.dev.k8s.local",   "content", {"namespaces": ["default","dev-app","dev-db"]},       1),
        ("staging",   "预发布环境",      "https://api.stg.k8s.local",  "content", {"namespaces": ["default","stg-app","stg-db"]},      2),
        ("production","生产环境",        "https://api.prd.k8s.local",  "content", {"namespaces": ["default","prd-app","prd-db","prd-monitor"]}, 3),
    ]
    created_envs = []
    for name, label, cluster_api, kc_type, ns_config, sort in envs_data:
        env, _ = await Environment.get_or_create(
            name=name,
            defaults=dict(
                label=label, cluster_api=cluster_api, kubeconfig="fake-kubeconfig-content",
                kubeconfig_type=kc_type, namespace_config=ns_config, sort_order=sort,
            ),
        )
        created_envs.append(env)
        print(f"  Env {'created' if _ else 'exists'}: {label}")

    # ── Env Permissions ──
    perm_pairs = [
        (created_users[0], created_envs[0]),  # admin → dev
        (created_users[0], created_envs[1]),  # admin → staging
        (created_users[0], created_envs[2]),  # admin → production
        (created_users[1], created_envs[0]),  # dev-zhang → dev
        (created_users[1], created_envs[1]),  # dev-zhang → staging
        (created_users[2], created_envs[0]),  # dev-li → dev
        (created_users[3], created_envs[1]),  # ops-wang → staging
        (created_users[3], created_envs[2]),  # ops-wang → production
    ]
    for user, env in perm_pairs:
        _, created = await EnvPermission.get_or_create(user=user, env=env)
        if created:
            print(f"  Permission: {user.username} → {env.name}")

    # ── Credentials ──
    creds_data = [
        (created_envs[0], "order-service-db", "mysql",     "10.100.1.10", 3306, "order_db",    "order_user",   "Order@2024Pass", "订单服务数据库"),
        (created_envs[0], "user-service-db",  "mysql",     "10.100.1.11", 3306, "user_db",     "user_user",    "User@2024Pass",  "用户服务数据库"),
        (created_envs[0], "cache-redis",      "redis",     "10.100.1.20", 6379, "0",           "default",      "Redis@2024Key",  "缓存 Redis"),
        (created_envs[1], "order-service-db", "mysql",     "10.100.2.10", 3306, "order_db",    "order_user",   "StgOrder#2024",  "订单服务数据库（预发布）"),
        (created_envs[1], "user-service-db",  "mysql",     "10.100.2.11", 3306, "user_db",     "user_user",    "StgUser#2024",   "用户服务数据库（预发布）"),
        (created_envs[1], "message-queue",    "rabbitmq",  "10.100.2.30", 5672, "vhost-order", "mq_user",      "MQ@Stg2024",     "消息队列"),
        (created_envs[2], "order-service-db", "mysql",     "10.100.3.10", 3306, "order_prod",  "order_admin",  "ProdOrder!2024!", "订单服务数据库（生产）"),
        (created_envs[2], "user-service-db",  "mysql",     "10.100.3.11", 3306, "user_prod",   "user_admin",   "ProdUser!2024!",  "用户服务数据库（生产）"),
        (created_envs[2], "monitor-db",       "postgresql","10.100.3.50", 5432, "monitor",     "mon_admin",    "Mon!Prod@2024",   "监控数据库"),
        (created_envs[2], "log-es",           "elasticsearch","10.100.3.60", 9200, "ksm-logs-*", "log_user",    "Log!Prod@2024",   "Elasticsearch 日志"),
    ]
    for env, svc, dbtype, host, port, dbname, user, passwd, desc in creds_data:
        enc_pw = aes_encrypt(passwd)
        cred, _ = await DBCredential.get_or_create(
            env=env, service_name=svc,
            defaults=dict(
                db_type=dbtype, host=host, port=port, database_name=dbname,
                username=user, password_encrypted=enc_pw, description=desc,
            ),
        )
        print(f"  Cred {'created' if _ else 'exists'}: {env.name}/{svc} ({dbtype})")

    # ── Toolbox Links ──
    links_data = [
        ("K8s Dashboard",     "https://dashboard.k8s.local",          "Monitor",    "k8s",     1),
        ("Grafana",           "https://grafana.k8s.local",            "DataV",      "k8s",     2),
        ("Prometheus",        "https://prometheus.k8s.local",         "Monitor",    "k8s",     3),
        ("Kibana",            "https://kibana.k8s.local",             "Search",     "k8s",     4),
        ("Harbor",            "https://harbor.k8s.local",             "Container",  "devops",  5),
        ("Jenkins",           "https://jenkins.k8s.local",            "Tools",      "devops",  6),
        ("SonarQube",         "https://sonarqube.k8s.local",          "Tools",      "devops",  7),
        ("ArgoCD",            "https://argocd.k8s.local",             "Deploy",     "devops",  8),
        ("Confluence",        "https://wiki.company.local",           "Document",   "internal",9),
        ("Jira",              "https://jira.company.local",           "Edit",       "internal",10),
        ("公司 GitLab",        "https://gitlab.company.local",         "Link",       "internal",11),
        ("腾讯云控制台",       "https://console.cloud.tencent.com",   "Cloud",      "cloud",   12),
        ("阿里云控制台",       "https://home.console.aliyun.com",      "Cloud",      "cloud",   13),
        ("华为云控制台",       "https://console.huaweicloud.com",      "Cloud",      "cloud",   14),
    ]
    for title, url, icon, category, sort in links_data:
        link, _ = await ToolboxLink.get_or_create(
            title=title, url=url,
            defaults=dict(icon=icon, category=category, sort_order=sort),
        )
        print(f"  Link {'created' if _ else 'exists'}: {title}")

    # ── Secret Cache Entries ──
    from datetime import datetime, timedelta, timezone
    secrets_data = [
        (created_envs[0], "default", "mysql-secret",      "Opaque", ["username","password","host"],     '{"username":"root","password":"dev-pass","host":"mysql.dev.svc"}'),
        (created_envs[0], "default", "redis-secret",      "Opaque", ["password"],                       '{"password":"dev-redis-pass"}'),
        (created_envs[0], "dev-app", "app-config",        "Opaque", ["config.yaml"],                    '{"config.yaml":"api_url: https://api.dev\\nlog_level: debug"}'),
        (created_envs[1], "default", "mysql-secret",      "Opaque", ["username","password","host"],     '{"username":"root","password":"stg-pass","host":"mysql.stg.svc"}'),
        (created_envs[1], "stg-app", "tls-cert",          "kubernetes.io/tls", ["tls.crt","tls.key"], '{"tls.crt":"---BEGIN CERTIFICATE---\\nfake-cert\\n---END CERTIFICATE---"}'),
        (created_envs[2], "default", "mysql-secret",      "Opaque", ["username","password","host"],     '{"username":"root","password":"prod-pass","host":"mysql.prd.svc"}'),
        (created_envs[2], "prd-app", "jwt-secret",        "Opaque", ["secret"],                         '{"secret":"prod-jwt-signing-key-2024"}'),
        (created_envs[2], "prd-app", "api-key",           "Opaque", ["api-key","api-secret"],           '{"api-key":"sk-prod-abc123","api-secret":"prod-secret-xyz"}'),
    ]
    for env, ns, sname, stype, keys, raw in secrets_data:
        cache, _ = await SecretCache.get_or_create(
            env=env, namespace=ns, secret_name=sname,
            defaults=dict(
                secret_type=stype, data_keys=keys, data_snapshot=raw,
                raw_data=raw, source_mode="sdk",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            ),
        )
        print(f"  SecretCache {'created' if _ else 'exists'}: {ns}/{sname}")

    # ── Summary ──
    print()
    print("=" * 50)
    print("Test data seeding complete!")
    print(f"  Users:        {await User.all().count()}")
    print(f"  Environments: {await Environment.all().count()}")
    print(f"  Credentials:  {await DBCredential.all().count()}")
    print(f"  ToolboxLinks: {await ToolboxLink.all().count()}")
    print(f"  Permissions:  {await EnvPermission.all().count()}")
    print(f"  SecretCaches: {await SecretCache.all().count()}")
    print("=" * 50)
    print()
    print("Default accounts:")
    print("  admin / admin123  (管理员)")
    print("  dev-zhang / dev123 (开发者)")
    print("  dev-li / dev123    (开发者)")
    print("  ops-wang / ops123  (运维)")
    print("  auditor / audit123 (审计)")
    print()
    print("Test environments: dev, staging, production")
    print("  10 credentials spread across all envs")
    print("  14 toolbox navigation links")
    print("  8 K8s secret cache entries")

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
