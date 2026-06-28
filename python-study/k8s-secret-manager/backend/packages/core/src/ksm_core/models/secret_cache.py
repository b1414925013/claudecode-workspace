from datetime import datetime, timezone
from tortoise import fields, models
from tortoise.indexes import Index


class SecretCache(models.Model):
    id = fields.BigIntField(pk=True)
    env = fields.ForeignKeyField("models.Environment", related_name="secret_caches")
    namespace = fields.CharField(max_length=128)
    secret_name = fields.CharField(max_length=256)
    secret_type = fields.CharField(max_length=64, default="Opaque")
    data_keys = fields.JSONField(default=list)
    data_snapshot = fields.TextField(null=True)
    raw_data = fields.TextField(null=True)
    source_mode = fields.CharField(max_length=16, default="sdk")
    fetched_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ksm_secret_cache"
        indexes = [
            Index(fields=["env_id"]),
            Index(fields=["namespace"]),
            Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
