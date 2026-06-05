package com.stockplatform.entity;

import com.mybatis-flex.core.annotation.Id;
import com.mybatis-flex.core.annotation.Table;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Table("positions")
public class Position {

    @Id
    private Integer id;

    private Integer accountId;

    private String stockCode;

    private String stockName;

    private Integer quantity;

    private Double avgCost;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}