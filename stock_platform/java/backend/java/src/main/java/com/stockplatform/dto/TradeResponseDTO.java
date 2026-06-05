package com.stockplatform.dto;

import com.stockplatform.entity.Trade;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class TradeResponseDTO {
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

    public static TradeResponseDTO fromEntity(Trade trade) {
        TradeResponseDTO dto = new TradeResponseDTO();
        dto.setId(trade.getId());
        dto.setAccountId(trade.getAccountId());
        dto.setStockCode(trade.getStockCode());
        dto.setStockName(trade.getStockName());
        dto.setTradeType(trade.getTradeType());
        dto.setQuantity(trade.getQuantity());
        dto.setPrice(trade.getPrice());
        dto.setCommission(trade.getCommission());
        dto.setTradeDate(trade.getTradeDate());
        dto.setProfit(trade.getProfit());
        dto.setCreatedAt(trade.getCreatedAt());
        return dto;
    }
}