package com.stockplatform.dto;

import lombok.Data;

@Data
public class SummaryDTO {
    private Integer totalAccounts;
    private Integer totalPositions;
    private Integer totalTrades;
    private Double totalCost;
    private Double totalProfit;
}