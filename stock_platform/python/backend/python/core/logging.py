import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    logger_name: str = "stock_platform",
) -> logging.Logger:
    """
    配置结构化日志

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_format: 日志格式 ("json" 或 "text")
        logger_name: 日志记录器名称
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def log_extra(**kwargs) -> dict:
    """为日志添加额外字段"""
    return kwargs