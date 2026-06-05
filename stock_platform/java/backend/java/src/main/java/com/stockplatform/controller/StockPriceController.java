package com.stockplatform.controller;

import com.stockplatform.dto.StockPriceHistoryDTO;
import com.stockplatform.dto.StockPriceResponseDTO;
import com.stockplatform.service.StockPriceService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/stock-prices")
public class StockPriceController {

    private final StockPriceService stockPriceService;

    public StockPriceController(StockPriceService stockPriceService) {
        this.stockPriceService = stockPriceService;
    }

    @PostMapping("/sync")
    public Map<String, String> syncAllPrices() {
        int count = stockPriceService.updateAllPositionsPrice();
        return Map.of("message", "成功更新 " + count + " 只股票价格");
    }

    @PostMapping("/{stockCode}")
    public StockPriceResponseDTO syncSinglePrice(@PathVariable String stockCode) {
        StockPriceResponseDTO result = stockPriceService.fetchAndSavePrice(stockCode);
        if (result == null) {
            throw new RuntimeException("获取价格失败");
        }
        return result;
    }

    @GetMapping("/{stockCode}/latest")
    public StockPriceResponseDTO getLatestPrice(@PathVariable String stockCode) {
        StockPriceResponseDTO result = stockPriceService.getLatestPrice(stockCode);
        if (result == null) {
            throw new RuntimeException("暂无价格数据");
        }
        return result;
    }

    @GetMapping("/{stockCode}/history")
    public StockPriceHistoryDTO getPriceHistory(@PathVariable String stockCode,
                                                 @RequestParam(defaultValue = "30") int days) {
        return stockPriceService.getPriceHistory(stockCode, days);
    }
}