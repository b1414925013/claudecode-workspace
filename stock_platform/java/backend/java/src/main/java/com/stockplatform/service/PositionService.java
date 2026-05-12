package com.stockplatform.service;

import com.my.mybatis.flex.core.condition.QueryCondition;
import com.stockplatform.dto.PositionCreateDTO;
import com.stockplatform.dto.PositionResponseDTO;
import com.stockplatform.entity.Position;
import com.stockplatform.entity.StockPrice;
import com.stockplatform.mapper.PositionMapper;
import com.stockplatform.mapper.StockPriceMapper;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class PositionService {

    private final PositionMapper positionMapper;
    private final StockPriceMapper stockPriceMapper;

    public PositionService(PositionMapper positionMapper, StockPriceMapper stockPriceMapper) {
        this.positionMapper = positionMapper;
        this.stockPriceMapper = stockPriceMapper;
    }

    public PositionResponseDTO createPosition(PositionCreateDTO dto) {
        Position position = new Position();
        position.setAccountId(dto.getAccountId());
        position.setStockCode(dto.getStockCode());
        position.setStockName(dto.getStockName());
        position.setQuantity(dto.getQuantity());
        position.setAvgCost(dto.getAvgCost());
        position.setCreatedAt(LocalDateTime.now());
        position.setUpdatedAt(LocalDateTime.now());
        positionMapper.insertSelective(position);
        return enrichPositionWithPrice(PositionResponseDTO.fromEntity(position));
    }

    public List<PositionResponseDTO> listPositions(Integer accountId) {
        QueryCondition condition = QueryCondition.create();
        if (accountId != null) {
            condition.where("account_id = ?", accountId);
        }
        return positionMapper.selectAllByCondition(condition).stream()
                .map(PositionResponseDTO::fromEntity)
                .map(this::enrichPositionWithPrice)
                .collect(Collectors.toList());
    }

    public List<PositionResponseDTO> listPositionsByAccount(Integer accountId) {
        QueryCondition condition = QueryCondition.create()
                .where("account_id = ?", accountId);
        return positionMapper.selectAllByCondition(condition).stream()
                .map(PositionResponseDTO::fromEntity)
                .map(this::enrichPositionWithPrice)
                .collect(Collectors.toList());
    }

    public PositionResponseDTO getPosition(Integer id) {
        Position position = positionMapper.selectOneById(id);
        if (position == null) {
            throw new RuntimeException("持仓不存在");
        }
        return enrichPositionWithPrice(PositionResponseDTO.fromEntity(position));
    }

    public PositionResponseDTO updatePosition(Integer id, PositionCreateDTO dto) {
        Position position = positionMapper.selectOneById(id);
        if (position == null) {
            throw new RuntimeException("持仓不存在");
        }

        int totalQuantity = position.getQuantity() + dto.getQuantity();
        if (totalQuantity > 0) {
            double totalCost = position.getQuantity() * position.getAvgCost()
                    + dto.getQuantity() * dto.getAvgCost();
            position.setAvgCost(totalCost / totalQuantity);
        }
        position.setQuantity(totalQuantity);
        position.setUpdatedAt(LocalDateTime.now());
        positionMapper.update(position);
        return enrichPositionWithPrice(PositionResponseDTO.fromEntity(position));
    }

    public void deletePosition(Integer id) {
        positionMapper.deleteById(id);
    }

    public long getPositionCount() {
        return positionMapper.selectCount(null);
    }

    private PositionResponseDTO enrichPositionWithPrice(PositionResponseDTO dto) {
        QueryCondition condition = QueryCondition.create()
                .where("stock_code = ?", dto.getStockCode())
                .orderBy("trade_date", true);
        List<StockPrice> prices = stockPriceMapper.selectAllByCondition(condition);
        if (!prices.isEmpty()) {
            StockPrice latest = prices.get(0);
            dto.setCurrentPrice(latest.getPrice());
            dto.setChangeValue(latest.getChangeValue());
            dto.setChangePercent(latest.getChangePercent());
            dto.setMarketValue(dto.getQuantity() * latest.getPrice());
        }
        return dto;
    }
}