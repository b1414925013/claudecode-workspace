package com.stockplatform.entity;

import com.mybatis-flex.core.annotation.Id;
import com.mybatis-flex.core.annotation.Table;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Table("stock_prices")
public class StockPrice {

    @Id
    private Integer id;

    private String stockCode;

    private Double price;

    private Double changeValue;

    private Double changePercent;

    private LocalDateTime tradeDate;

    private LocalDateTime createdAt;
}