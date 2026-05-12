package com.stockplatform.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class PositionCreateDTO {

    @NotNull(message = "账户ID不能为空")
    private Integer accountId;

    @NotBlank(message = "股票代码不能为空")
    private String stockCode;

    @NotBlank(message = "股票名称不能为空")
    private String stockName;

    @NotNull(message = "数量不能为空")
    private Integer quantity;

    @NotNull(message = "平均成本不能为空")
    private Double avgCost;
}