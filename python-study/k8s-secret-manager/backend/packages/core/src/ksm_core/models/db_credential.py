from tortoise import fields, models
from tortoise.indexes import Index


class DBCredential(models.Model):
    id = fields.BigIntField(pk=True)
    env = fields.ForeignKeyField("models.Environment", related_name="credentials")
    service_name = fields.CharField(max_length=128)
    db_type = fields.CharField(max_length=16, default="mysql")
    host = fields.CharField(max_length=256)
    port = fields.IntField()
    database_name = fields.CharField(max_length=128, null=True)
    username = fields.CharField(max_length=128)
    password_encrypted = fields.CharField(max_length=512)
    extra_params = fields.JSONField(null=True)
    description = fields.CharField(max_length=512, null=True)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ksm_db_credentials"
        indexes = [
            Index(fields=["env_id"]),
            Index(fields=["service_name"]),
            Index(fields=["db_type"]),
        ]
