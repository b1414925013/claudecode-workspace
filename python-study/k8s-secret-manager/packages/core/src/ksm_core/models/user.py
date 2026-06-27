from tortoise import fields, models
from tortoise.indexes import Index


class User(models.Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=64, unique=True)
    password_hash = fields.CharField(max_length=256)
    nickname = fields.CharField(max_length=64, null=True)
    email = fields.CharField(max_length=128, null=True)
    phone = fields.CharField(max_length=20, null=True)
    role = fields.CharField(max_length=16, default="developer")
    is_active = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ksm_users"
        indexes = [Index(fields=["role"]), Index(fields=["is_active"])]

    class PydanticMeta:
        exclude = ["password_hash", "is_deleted"]
