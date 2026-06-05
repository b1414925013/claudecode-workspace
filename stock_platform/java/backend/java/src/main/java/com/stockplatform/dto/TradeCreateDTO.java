package com.stockplatform.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class TradeCreateDTO {

    @NotNull(message = "账户ID不能为空")
    private Integer accountId;

    @NotBlank(message = "股票代码不能为空")
    private String stockCode;

    @NotBlank(message = "股票名称不能为空")
    private String stockName;

    @NotBlank(message = "交易类型不能为空")
    private String tradeType;

    @NotNull(message = "数量不能为空")
    private Integer quantity;

    @NotNull(message = "价格不能为空")
    private Double price;

    private Double commission = 0.0;

    @NotNull(message = "交易日期不能为空")
    private LocalDateTime tradeDate;
}