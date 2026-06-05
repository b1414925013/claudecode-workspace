package com.stockplatform.entity;

import com.mybatis-flex.core.annotation.Id;
import com.mybatis-flex.core.annotation.Table;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Table("dividends")
public class Dividend {

    @Id
    private Integer id;

    private Integer accountId;

    private String stockCode;

    private String stockName;

    private Double dividendAmount;

    private LocalDateTime dividendDate;

    private LocalDateTime createdAt;
}