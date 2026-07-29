# NumUtil 数值工具

`pyhutool.core.NumUtil` 对齐 Hutool `cn.hutool.core.util.NumberUtil`。

!!! note "精度"
    算术运算内部使用 `decimal.Decimal`（对应 Hutool 的 `BigDecimal`），返回值为 `Decimal`。
    关键特性：`NumUtil.add(0.1, 0.2) == Decimal("0.3")`，消除浮点误差。

## 算术

```python
NumUtil.add(0.1, 0.2)       # Decimal("0.3")
NumUtil.add(1, 2, 3)        # Decimal(6)
NumUtil.sub(10, 3, 2)       # Decimal(5)
NumUtil.mul(2, 3, 4)        # Decimal(24)
NumUtil.div(10, 4, scale=2) # Decimal("2.50")
NumUtil.div(1, 3, scale=2)  # Decimal("0.33")
```

## 四舍五入

```python
NumUtil.round(3.14159, 2)    # Decimal("3.14")
NumUtil.round(3.145, 2)       # Decimal("3.15")
NumUtil.round_str(3.14159, 2) # "3.14"
```

## DecimalFormat 风格

```python
NumUtil.decimal_format(3.14159, "0.00")   # "3.14"
NumUtil.decimal_format(3.1, "0.00")       # "3.10"
NumUtil.decimal_format(3.14159, "0.##")   # "3.14"
NumUtil.decimal_format(3.1, "0.##")        # "3.1"
NumUtil.decimal_format(3.99, "0")          # "4"  （四舍五入）
```

## 判断

```python
NumUtil.is_number("123")      # True
NumUtil.is_number("1e10")     # True
NumUtil.is_number("abc")      # False
NumUtil.is_integer("12.3")    # False
NumUtil.is_integer(12.0)      # True
```

## 转换

```python
NumUtil.to_int("123")          # 123
NumUtil.to_int("abc", -1)     # -1
NumUtil.to_double("3.14")     # 3.14
NumUtil.to_str(Decimal("3.14"))  # "3.14"
NumUtil.null_to_zero(None)    # Decimal(0)
```

## 极值

```python
NumUtil.max(1, 2, 3)   # Decimal(3)
NumUtil.min(1, 2, 3)   # Decimal(1)
```
