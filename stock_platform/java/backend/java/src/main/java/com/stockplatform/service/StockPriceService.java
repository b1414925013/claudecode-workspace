package com.stockplatform.service;

import com.my.mybatis.flex.core.condition.QueryCondition;
import com.stockplatform.dto.StockPriceHistoryDTO;
import com.stockplatform.dto.StockPriceResponseDTO;
import com.stockplatform.entity.Position;
import com.stockplatform.entity.StockPrice;
import com.stockplatform.mapper.PositionMapper;
import com.stockplatform.mapper.StockPriceMapper;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class StockPriceService {

    private final StockPriceMapper stockPriceMapper;
    private final PositionMapper positionMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    public StockPriceService(StockPriceMapper stockPriceMapper, PositionMapper positionMapper) {
        this.stockPriceMapper = stockPriceMapper;
        this.positionMapper = positionMapper;
    }

    public StockPriceResponseDTO fetchAndSavePrice(String stockCode) {
        Map<String, Object> data = fetchStockPriceFromApi(stockCode);
        if (data == null || data.get("price") == null) {
            return null;
        }

        StockPrice stockPrice = new StockPrice();
        stockPrice.setStockCode(stockCode);
        stockPrice.setPrice((Double) data.get("price"));
        stockPrice.setChangeValue((Double) data.get("changeValue"));
        stockPrice.setChangePercent((Double) data.get("changePercent"));
        stockPrice.setTradeDate(LocalDateTime.now());
        stockPrice.setCreatedAt(LocalDateTime.now());
        stockPriceMapper.insertSelective(stockPrice);

        return StockPriceResponseDTO.fromEntity(stockPrice);
    }

    public int updateAllPositionsPrice() {
        List<Position> positions = positionMapper.selectAll();
        Set<String> stockCodes = positions.stream()
                .map(Position::getStockCode)
                .collect(Collectors.toSet());

        int count = 0;
        for (String code : stockCodes) {
            if (fetchAndSavePrice(code) != null) {
                count++;
            }
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        return count;
    }

    @Scheduled(cron = "0 0 16 * * *")
    public void scheduledUpdatePrices() {
        updateAllPositionsPrice();
    }

    public StockPriceResponseDTO getLatestPrice(String stockCode) {
        QueryCondition condition = QueryCondition.create()
                .where("stock_code = ?", stockCode)
                .orderBy("trade_date", true);
        List<StockPrice> prices = stockPriceMapper.selectAllByCondition(condition);
        if (prices.isEmpty()) {
            return null;
        }
        return StockPriceResponseDTO.fromEntity(prices.get(0));
    }

    public StockPriceHistoryDTO getPriceHistory(String stockCode, int days) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(days);
        QueryCondition condition = QueryCondition.create()
                .where("stock_code = ?", stockCode)
                .where("trade_date >= ?", startDate)
                .orderBy("trade_date", true);
        List<StockPrice> prices = stockPriceMapper.selectAllByCondition(condition);

        StockPriceHistoryDTO historyDTO = new StockPriceHistoryDTO();
        historyDTO.setStockCode(stockCode);
        historyDTO.setPrices(prices.stream()
                .map(StockPriceResponseDTO::fromEntity)
                .collect(Collectors.toList()));
        return historyDTO;
    }

    private Map<String, Object> fetchStockPriceFromApi(String stockCode) {
        try {
            String emCode = getEastmoneyCode(stockCode);
            String url = "https://push2.eastmoney.com/api/qt/stock/get?secid=" + emCode + "&fields=f43,f44,f57,f58";

            String response = restTemplate.getForObject(url, String.class);

            Map<String, Object> result = new HashMap<>();
            // 简单解析 JSON - 实际应该用 Jackson 或 Gson
            // 这里仅作示例，实际需要更完善的实现
            // 暂时返回 null，后续可以添加完整的 JSON 解析
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private String getEastmoneyCode(String stockCode) {
        if (stockCode.startsWith("6")) {
            return "1." + stockCode;
        } else if (stockCode.startsWith("0") || stockCode.startsWith("3")) {
            return "0." + stockCode;
        }
        return stockCode;
    }
}