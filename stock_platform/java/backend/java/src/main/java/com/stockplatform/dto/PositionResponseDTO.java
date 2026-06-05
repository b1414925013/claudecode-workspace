package com.stockplatform.dto;

import com.stockplatform.entity.Position;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class PositionResponseDTO {
    private Integer id;
    private Integer accountId;
    private String stockCode;
    private String stockName;
    private Integer quantity;
    private Double avgCost;
    private Double currentPrice;
    private Double changeValue;
    private Double changePercent;
    private Double marketValue;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static PositionResponseDTO fromEntity(Position position) {
        PositionResponseDTO dto = new PositionResponseDTO();
        dto.setId(position.getId());
        dto.setAccountId(position.getAccountId());
        dto.setStockCode(position.getStockCode());
        dto.setStockName(position.getStockName());
        dto.setQuantity(position.getQuantity());
        dto.setAvgCost(position.getAvgCost());
        dto.setCreatedAt(position.getCreatedAt());
        dto.setUpdatedAt(position.getUpdatedAt());
        return dto;
    }
}