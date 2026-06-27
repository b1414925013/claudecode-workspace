-- ============================================
-- K8s Secret Manager - Database Initialization DDL
-- ============================================

CREATE DATABASE IF NOT EXISTS ksm_secret_manager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ksm_secret_manager;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS ksm_users (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(64)  NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash   VARCHAR(256) NOT NULL COMMENT 'bcrypt 哈希密码',
    nickname        VARCHAR(64)  DEFAULT NULL COMMENT '显示昵称',
    email           VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    phone           VARCHAR(20)  DEFAULT NULL COMMENT '手机号',
    role            VARCHAR(16)  NOT NULL DEFAULT 'developer' COMMENT 'admin|developer',
    is_active       TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '是否启用',
    is_deleted      TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '软删除标记',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 环境表（K8s 集群环境）
CREATE TABLE IF NOT EXISTS ksm_environments (
    id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(64)  NOT NULL UNIQUE COMMENT '环境名称 dev/test/staging/prod',
    label            VARCHAR(128) NOT NULL COMMENT '显示标签',
    cluster_api      VARCHAR(256) NOT NULL COMMENT 'K8s API Server 地址',
    kubeconfig       TEXT         NOT NULL COMMENT 'kubeconfig 凭证内容',
    kubeconfig_type  VARCHAR(16)  NOT NULL DEFAULT 'content' COMMENT 'content|path',
    namespace_config JSON         NOT NULL COMMENT '命名空间说明 JSON',
    k8s_sdk_mode     VARCHAR(16)  NOT NULL DEFAULT 'auto' COMMENT 'sdk|kubectl|auto',
    sort_order       INT          NOT NULL DEFAULT 0 COMMENT '排序号',
    is_deleted       TINYINT(1)   NOT NULL DEFAULT 0,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_env_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='K8s 环境配置表';

-- 3. 数据库凭据表
CREATE TABLE IF NOT EXISTS ksm_db_credentials (
    id                 BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    env_id             BIGINT UNSIGNED NOT NULL COMMENT '所属环境 ID',
    service_name       VARCHAR(128) NOT NULL COMMENT '服务名称',
    db_type            VARCHAR(16)  NOT NULL DEFAULT 'mysql' COMMENT 'mysql|redis|postgresql|mongodb|other',
    host               VARCHAR(256) NOT NULL COMMENT '连接地址',
    port               INT          NOT NULL COMMENT '端口',
    database_name      VARCHAR(128) DEFAULT NULL COMMENT '数据库名',
    username           VARCHAR(128) NOT NULL COMMENT '用户名',
    password_encrypted VARCHAR(512) NOT NULL COMMENT 'AES 加密后的密码',
    extra_params       JSON         DEFAULT NULL COMMENT '额外连接参数',
    description        VARCHAR(512) DEFAULT NULL COMMENT '备注说明',
    is_deleted         TINYINT(1)   NOT NULL DEFAULT 0,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_db_env (env_id),
    INDEX idx_db_service (service_name),
    INDEX idx_db_type (db_type),
    CONSTRAINT fk_db_env FOREIGN KEY (env_id) REFERENCES ksm_environments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库凭据表';

-- 4. K8s Secret 缓存表
CREATE TABLE IF NOT EXISTS ksm_secret_cache (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    env_id          BIGINT UNSIGNED NOT NULL COMMENT '所属环境 ID',
    namespace       VARCHAR(128) NOT NULL COMMENT '命名空间',
    secret_name     VARCHAR(256) NOT NULL COMMENT 'Secret 名称',
    secret_type     VARCHAR(64)  DEFAULT 'Opaque' COMMENT 'Secret 类型',
    data_keys       JSON         NOT NULL COMMENT '包含的 key 列表',
    data_snapshot   LONGTEXT     DEFAULT NULL COMMENT '解密后的键值快照',
    raw_data        LONGTEXT     DEFAULT NULL COMMENT '原始 Base64 编码数据',
    source_mode     VARCHAR(16)  NOT NULL DEFAULT 'sdk' COMMENT 'sdk|kubectl',
    fetched_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '拉取时间',
    expires_at      DATETIME     NOT NULL COMMENT '过期时间',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sc_env (env_id),
    INDEX idx_sc_namespace (namespace),
    INDEX idx_sc_expires (expires_at),
    CONSTRAINT fk_sc_env FOREIGN KEY (env_id) REFERENCES ksm_environments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='K8s Secret 缓存表';

-- 5. 操作审计日志表
CREATE TABLE IF NOT EXISTS ksm_audit_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED DEFAULT NULL COMMENT '操作用户 ID',
    username        VARCHAR(64)  NOT NULL COMMENT '操作用户名',
    action          VARCHAR(64)  NOT NULL COMMENT '操作类型',
    resource_type   VARCHAR(64)  NOT NULL COMMENT '资源类型',
    resource_id     VARCHAR(128) DEFAULT NULL COMMENT '资源 ID',
    resource_name   VARCHAR(256) DEFAULT NULL COMMENT '资源名称',
    detail          JSON         DEFAULT NULL COMMENT '操作详情',
    ip_address      VARCHAR(45)  DEFAULT NULL COMMENT '请求 IP',
    user_agent      VARCHAR(512) DEFAULT NULL COMMENT 'UA',
    status          VARCHAR(16)  NOT NULL DEFAULT 'success' COMMENT 'success|failure',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_al_user (user_id),
    INDEX idx_al_action (action),
    INDEX idx_al_resource (resource_type, resource_id),
    INDEX idx_al_created (created_at),
    CONSTRAINT fk_al_user FOREIGN KEY (user_id) REFERENCES ksm_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作审计日志表';

-- 6. 工具箱-导航链接表
CREATE TABLE IF NOT EXISTS ksm_toolbox_links (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(128) NOT NULL COMMENT '链接标题',
    url           VARCHAR(512) NOT NULL COMMENT '链接地址',
    icon          VARCHAR(64)  DEFAULT 'Link' COMMENT '图标名',
    category      VARCHAR(64)  NOT NULL DEFAULT 'default' COMMENT '分类',
    sort_order    INT          NOT NULL DEFAULT 0,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tl_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导航链接表';

-- 7. 环境-用户授权表
CREATE TABLE IF NOT EXISTS ksm_env_permissions (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT UNSIGNED NOT NULL,
    env_id        BIGINT UNSIGNED NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_env (user_id, env_id),
    CONSTRAINT fk_ep_user FOREIGN KEY (user_id) REFERENCES ksm_users(id),
    CONSTRAINT fk_ep_env  FOREIGN KEY (env_id)  REFERENCES ksm_environments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='环境授权表';
