package com.stockplatform.service;

import com.my.mybatis.flex.core.condition.QueryCondition;
import com.stockplatform.dto.StatisticsDTO;
import com.stockplatform.dto.SummaryDTO;
import com.stockplatform.entity.Account;
import com.stockplatform.entity.Position;
import com.stockplatform.entity.StockPrice;
import com.stockplatform.entity.Trade;
import com.stockplatform.mapper.AccountMapper;
import com.stockplatform.mapper.PositionMapper;
import com.stockplatform.mapper.StockPriceMapper;
import com.stockplatform.mapper.TradeMapper;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class StatisticsService {

    private final PositionMapper positionMapper;
    private final TradeMapper tradeMapper;
    private final StockPriceMapper stockPriceMapper;
    private final AccountMapper accountMapper;

    public StatisticsService(PositionMapper positionMapper, TradeMapper tradeMapper,
                              StockPriceMapper stockPriceMapper, AccountMapper accountMapper) {
        this.positionMapper = positionMapper;
        this.tradeMapper = tradeMapper;
        this.stockPriceMapper = stockPriceMapper;
        this.accountMapper = accountMapper;
    }

    public StatisticsDTO getStatistics(Integer accountId, LocalDateTime startDate, LocalDateTime endDate) {
        QueryCondition positionCondition = QueryCondition.create();
        if (accountId != null) {
            positionCondition.where("account_id = ?", accountId);
        }
        List<Position> positions = positionMapper.selectAllByCondition(positionCondition);

        double totalCost = 0;
        double totalMarketValue = 0;
        for (Position pos : positions) {
            totalCost += pos.getQuantity() * pos.getAvgCost();
            StockPrice price = getLatestPrice(pos.getStockCode());
            if (price != null) {
                totalMarketValue += pos.getQuantity() * price.getPrice();
            }
        }

        double totalProfit = totalMarketValue - totalCost;
        double returnRate = totalCost > 0 ? totalProfit / totalCost : 0;

        QueryCondition tradeCondition = QueryCondition.create();
        if (accountId != null) {
            tradeCondition.where("account_id = ?", accountId);
        }
        if (startDate != null) {
            tradeCondition.where("trade_date >= ?", startDate);
        }
        if (endDate != null) {
            tradeCondition.where("trade_date <= ?", endDate);
        }
        List<Trade> trades = tradeMapper.selectAllByCondition(tradeCondition);

        int winningTrades = 0;
        int sellTrades = 0;
        for (Trade trade : trades) {
            if ("sell".equalsIgnoreCase(trade.getTradeType())) {
                sellTrades++;
                if (trade.getProfit() != null && trade.getProfit() > 0) {
                    winningTrades++;
                }
            }
        }
        double winRate = sellTrades > 0 ? (double) winningTrades / sellTrades : 0;

        StatisticsDTO dto = new StatisticsDTO();
        dto.setTotalProfit(totalProfit);
        dto.setTotalCost(totalCost);
        dto.setTotalMarketValue(totalMarketValue);
        dto.setReturnRate(returnRate);
        dto.setWinRate(winRate);
        dto.setTotalTrades(sellTrades);
        dto.setWinningTrades(winningTrades);
        dto.setLosingTrades(sellTrades - winningTrades);
        dto.setAvgHoldingDays(0.0);
        return dto;
    }

    public SummaryDTO getSummary() {
        List<Account> accounts = accountMapper.selectAll();
        List<Position> positions = positionMapper.selectAll();
        List<Trade> trades = tradeMapper.selectAll();

        double totalCost = 0;
        double totalMarketValue = 0;
        for (Position pos : positions) {
            totalCost += pos.getQuantity() * pos.getAvgCost();
            StockPrice price = getLatestPrice(pos.getStockCode());
            if (price != null) {
                totalMarketValue += pos.getQuantity() * price.getPrice();
            }
        }

        double totalProfit = totalMarketValue - totalCost;

        SummaryDTO dto = new SummaryDTO();
        dto.setTotalAccounts(accounts.size());
        dto.setTotalPositions(positions.size());
        dto.setTotalTrades(trades.size());
        dto.setTotalCost(totalCost);
        dto.setTotalProfit(totalProfit);
        return dto;
    }

    private StockPrice getLatestPrice(String stockCode) {
        QueryCondition condition = QueryCondition.create()
                .where("stock_code = ?", stockCode)
                .orderBy("trade_date", true);
        List<StockPrice> prices = stockPriceMapper.selectAllByCondition(condition);
        return prices.isEmpty() ? null : prices.get(0);
    }
}