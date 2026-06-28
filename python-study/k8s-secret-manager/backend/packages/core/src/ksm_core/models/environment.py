from tortoise import fields, models
from tortoise.indexes import Index


class Environment(models.Model):
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=64, unique=True)
    label = fields.CharField(max_length=128)
    cluster_api = fields.CharField(max_length=256)
    kubeconfig = fields.TextField()
    kubeconfig_type = fields.CharField(max_length=16, default="content")
    namespace_config = fields.JSONField(default=dict)
    k8s_sdk_mode = fields.CharField(max_length=16, default="auto")
    sort_order = fields.IntField(default=0)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ksm_environments"
        indexes = [Index(fields=["is_deleted"])]

    class PydanticMeta:
        exclude = ["kubeconfig"]
