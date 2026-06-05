package com.stockplatform.dto;

import com.stockplatform.entity.Dividend;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class DividendResponseDTO {
    private Integer id;
    private Integer accountId;
    private String stockCode;
    private String stockName;
    private Double dividendAmount;
    private LocalDateTime dividendDate;
    private LocalDateTime createdAt;

    public static DividendResponseDTO fromEntity(Dividend dividend) {
        DividendResponseDTO dto = new DividendResponseDTO();
        dto.setId(dividend.getId());
        dto.setAccountId(dividend.getAccountId());
        dto.setStockCode(dividend.getStockCode());
        dto.setStockName(dividend.getStockName());
        dto.setDividendAmount(dividend.getDividendAmount());
        dto.setDividendDate(dividend.getDividendDate());
        dto.setCreatedAt(dividend.getCreatedAt());
        return dto;
    }
}