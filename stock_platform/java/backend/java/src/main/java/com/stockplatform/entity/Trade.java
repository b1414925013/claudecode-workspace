package com.stockplatform.entity;

import com.mybatis-flex.core.annotation.Id;
import com.mybatis-flex.core.annotation.Table;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Table("trades")
public class Trade {

    @Id
    private Integer id;

    private Integer accountId;

    private String stockCode;

    private String stockName;

    private String tradeType;

    private Integer quantity;

    private Double price;

    private Double commission;

    private LocalDateTime tradeDate;

    private Double profit;

    private LocalDateTime createdAt;
}