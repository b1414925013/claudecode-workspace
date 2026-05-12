from tortoise import Model, fields


class Account(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    name = fields.CharField(max_length=100)
    account_type = fields.CharField(max_length=20, default="cash")
    created_at = fields.DatetimeField(auto_now_add=True)

    positions: fields.ReverseRelation["Position"]
    trades: fields.ReverseRelation["Trade"]
    dividends: fields.ReverseRelation["Dividend"]

    class Meta:
        table = "accounts"


class Position(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKey(
        "models.Account", on_delete="CASCADE"
    )
    account_id: int
    stock_code = fields.CharField(max_length=20)
    stock_name = fields.CharField(max_length=100)
    quantity = fields.IntField()
    avg_cost = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "positions"


class Trade(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKey(
        "models.Account", on_delete="CASCADE"
    )
    account_id: int
    stock_code = fields.CharField(max_length=20)
    stock_name = fields.CharField(max_length=100)
    trade_type = fields.CharField(max_length=10)  # buy 或 sell
    quantity = fields.IntField()
    price = fields.FloatField()
    commission = fields.FloatField(default=0.0)
    trade_date = fields.DatetimeField()
    profit = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "trades"


class Dividend(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKey(
        "models.Account", on_delete="CASCADE"
    )
    account_id: int
    stock_code = fields.CharField(max_length=20)
    stock_name = fields.CharField(max_length=100)
    dividend_amount = fields.FloatField()
    dividend_date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "dividends"


class StockPrice(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    stock_code = fields.CharField(max_length=20, index=True)
    price = fields.FloatField()
    change_value = fields.FloatField(null=True)
    change_percent = fields.FloatField(null=True)
    trade_date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "stock_prices"