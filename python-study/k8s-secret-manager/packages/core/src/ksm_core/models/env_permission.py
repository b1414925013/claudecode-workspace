from tortoise import fields, models


class EnvPermission(models.Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="env_permissions")
    env = fields.ForeignKeyField("models.Environment", related_name="user_permissions")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ksm_env_permissions"
        unique_together = (("user_id", "env_id"),)
