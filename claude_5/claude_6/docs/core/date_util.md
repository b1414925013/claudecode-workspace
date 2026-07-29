# DateUtil 日期时间工具

`pyhutool.core.DateUtil` 对齐 Hutool `cn.hutool.core.date.DateUtil`。

## 当前时间

```python
DateUtil.date()              # datetime.now()
DateUtil.now()               # "2026-07-24 12:30:45"
DateUtil.today()             # "2026-07-24"
DateUtil.current()           # 毫秒时间戳
```

## 格式化与解析（Java 模式）

支持 Java `SimpleDateFormat` 风格模式串，内部自动转换：

```python
d = datetime(2026, 7, 24, 12, 30, 45)
DateUtil.format(d, "yyyy-MM-dd HH:mm:ss")   # "2026-07-24 12:30:45"
DateUtil.format_date(d)                     # "2026-07-24"
DateUtil.format_time(d)                     # "12:30:45"

DateUtil.parse("2026-07-24 12:30:45")       # datetime
DateUtil.parse_date("2026-07-24")            # datetime
DateUtil.parse_utc("2026-01-01T00:00:00+08:00")
```

## 时间戳

```python
DateUtil.to_epoch_ms(d)     # 毫秒时间戳
DateUtil.to_epoch_sec(d)    # 秒时间戳
DateUtil.from_epoch_ms(ms)  # 由毫秒构造 datetime
```

## 偏移

```python
DateUtil.offset(d, DateField.YEAR, 1)        # +1 年
DateUtil.offset(d, DateField.MONTH, 3)       # +3 月（自动跨年）
DateUtil.offset_day(d, 5)                    # +5 天
DateUtil.offset_hour(d, -2)                  # -2 小时
```

## 区间边界

```python
DateUtil.begin_of_day(d)    # 00:00:00
DateUtil.end_of_day(d)      # 23:59:59.999999
DateUtil.begin_of_month(d)
DateUtil.end_of_month(d)
```

## 取值 / 判断

```python
DateUtil.day_of_week(d)     # 1=周日 ... 7=周六（Java Calendar 风格）
DateUtil.day_of_year(d)
DateUtil.is_leap_year(2024)  # True
DateUtil.is_same_day(d1, d2)
```

## 区间计算

```python
DateUtil.between(d1, d2, DateUnit.DAY)      # 天差（绝对值）
DateUtil.between(d1, d2, DateUnit.SECOND)
DateUtil.between_ms(d1, d2)
DateUtil.between_day(d1, d2)
```

!!! note "星期约定"
    `day_of_week` 采用 Java `Calendar` 风格：周日=1，周一=2，...，周六=7，与 Python `weekday()`（周一=0）不同。
