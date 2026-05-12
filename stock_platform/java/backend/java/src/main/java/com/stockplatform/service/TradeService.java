package com.stockplatform.service;

import com.my.mybatis.flex.core.condition.QueryCondition;
import com.stockplatform.dto.TradeCreateDTO;
import com.stockplatform.dto.TradeResponseDTO;
import com.stockplatform.entity.Position;
import com.stockplatform.entity.Trade;
import com.stockplatform.mapper.PositionMapper;
import com.stockplatform.mapper.TradeMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class TradeService {

    private final TradeMapper tradeMapper;
    private final PositionMapper positionMapper;

    public TradeService(TradeMapper tradeMapper, PositionMapper positionMapper) {
        this.tradeMapper = tradeMapper;
        this.positionMapper = positionMapper;
    }

    @Transactional
    public TradeResponseDTO createTrade(TradeCreateDTO dto) {
        Trade trade = new Trade();
        trade.setAccountId(dto.getAccountId());
        trade.setStockCode(dto.getStockCode());
        trade.setStockName(dto.getStockName());
        trade.setTradeType(dto.getTradeType());
        trade.setQuantity(dto.getQuantity());
        trade.setPrice(dto.getPrice());
        trade.setCommission(dto.getCommission() != null ? dto.getCommission() : 0.0);
        trade.setTradeDate(dto.getTradeDate());
        trade.setCreatedAt(LocalDateTime.now());
        tradeMapper.insertSelective(trade);

        QueryCondition positionCondition = QueryCondition.create()
                .where("account_id = ?", dto.getAccountId())
                .where("stock_code = ?", dto.getStockCode());
        Position position = positionMapper.selectOneByCondition(positionCondition);

        if ("buy".equalsIgnoreCase(dto.getTradeType())) {
            if (position != null) {
                int totalQuantity = position.getQuantity() + dto.getQuantity();
                double totalCost = position.getQuantity() * position.getAvgCost()
                        + dto.getQuantity() * dto.getPrice();
                position.setAvgCost(totalCost / totalQuantity);
                position.setQuantity(totalQuantity);
                position.setUpdatedAt(LocalDateTime.now());
                positionMapper.update(position);
            } else {
                position = new Position();
                position.setAccountId(dto.getAccountId());
                position.setStockCode(dto.getStockCode());
                position.setStockName(dto.getStockName());
                position.setQuantity(dto.getQuantity());
                position.setAvgCost(dto.getPrice());
                position.setCreatedAt(LocalDateTime.now());
                position.setUpdatedAt(LocalDateTime.now());
                positionMapper.insertSelective(position);
            }
        } else if ("sell".equalsIgnoreCase(dto.getTradeType())) {
            if (position != null) {
                double profit = (dto.getPrice() - position.getAvgCost()) * dto.getQuantity()
                        - (dto.getCommission() != null ? dto.getCommission() : 0.0);
                trade.setProfit(profit);
                tradeMapper.update(trade);

                position.setQuantity(position.getQuantity() - dto.getQuantity());
                position.setUpdatedAt(LocalDateTime.now());
                if (position.getQuantity() <= 0) {
                    positionMapper.deleteById(position.getId());
                } else {
                    positionMapper.update(position);
                }
            }
        }

        return TradeResponseDTO.fromEntity(trade);
    }

    public List<TradeResponseDTO> listTrades(Integer accountId, LocalDateTime startDate, LocalDateTime endDate) {
        QueryCondition condition = QueryCondition.create();
        if (accountId != null) {
            condition.where("account_id = ?", accountId);
        }
        if (startDate != null) {
            condition.where("trade_date >= ?", startDate);
        }
        if (endDate != null) {
            condition.where("trade_date <= ?", endDate);
        }
        condition.orderBy("trade_date", false);

        return tradeMapper.selectAllByCondition(condition).stream()
                .map(TradeResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    public long getTradeCount() {
        return tradeMapper.selectCount(null);
    }
}