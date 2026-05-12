package com.stockplatform.dto;

import com.stockplatform.entity.StockPrice;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class StockPriceResponseDTO {
    private Integer id;
    private String stockCode;
    private Double price;
    private Double changeValue;
    private Double changePercent;
    private LocalDateTime tradeDate;
    private LocalDateTime createdAt;

    public static StockPriceResponseDTO fromEntity(StockPrice stockPrice) {
        StockPriceResponseDTO dto = new StockPriceResponseDTO();
        dto.setId(stockPrice.getId());
        dto.setStockCode(stockPrice.getStockCode());
        dto.setPrice(stockPrice.getPrice());
        dto.setChangeValue(stockPrice.getChangeValue());
        dto.setChangePercent(stockPrice.getChangePercent());
        dto.setTradeDate(stockPrice.getTradeDate());
        dto.setCreatedAt(stockPrice.getCreatedAt());
        return dto;
    }
}