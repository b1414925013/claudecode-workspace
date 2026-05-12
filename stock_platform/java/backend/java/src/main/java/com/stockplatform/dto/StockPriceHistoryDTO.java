package com.stockplatform.dto;

import lombok.Data;
import java.util.List;

@Data
public class StockPriceHistoryDTO {
    private String stockCode;
    private List<StockPriceResponseDTO> prices;
}