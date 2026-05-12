package com.stockplatform.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class DividendCreateDTO {

    @NotNull(message = "账户ID不能为空")
    private Integer accountId;

    @NotBlank(message = "股票代码不能为空")
    private String stockCode;

    @NotBlank(message = "股票名称不能为空")
    private String stockName;

    @NotNull(message = "分红金额不能为空")
    private Double dividendAmount;

    @NotNull(message = "分红日期不能为空")
    private LocalDateTime dividendDate;
}