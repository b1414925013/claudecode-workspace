package com.stockplatform.dto;

import lombok.Data;

@Data
public class StatisticsDTO {
    private Double totalProfit;
    private Double totalCost;
    private Double totalMarketValue;
    private Double returnRate;
    private Double winRate;
    private Integer totalTrades;
    private Integer winningTrades;
    private Integer losingTrades;
    private Double avgHoldingDays;
}