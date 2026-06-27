from tortoise import fields, models
from tortoise.indexes import Index


class AuditLog(models.Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", null=True, related_name="audit_logs")
    username = fields.CharField(max_length=64)
    action = fields.CharField(max_length=64)
    resource_type = fields.CharField(max_length=64)
    resource_id = fields.CharField(max_length=128, null=True)
    resource_name = fields.CharField(max_length=256, null=True)
    detail = fields.JSONField(null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    user_agent = fields.CharField(max_length=512, null=True)
    status = fields.CharField(max_length=16, default="success")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ksm_audit_logs"
        indexes = [
            Index(fields=["user_id"]),
            Index(fields=["action"]),
            Index(fields=["resource_type", "resource_id"]),
            Index(fields=["created_at"]),
        ]
