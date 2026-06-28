from tortoise import fields, models


class ToolboxLink(models.Model):
    id = fields.BigIntField(pk=True)
    title = fields.CharField(max_length=128)
    url = fields.CharField(max_length=512)
    icon = fields.CharField(max_length=64, default="Link")
    category = fields.CharField(max_length=64, default="default")
    sort_order = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ksm_toolbox_links"
