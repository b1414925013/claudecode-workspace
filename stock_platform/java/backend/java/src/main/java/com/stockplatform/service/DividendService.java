package com.stockplatform.service;

import com.my.mybatis.flex.core.condition.QueryCondition;
import com.stockplatform.dto.DividendCreateDTO;
import com.stockplatform.dto.DividendResponseDTO;
import com.stockplatform.entity.Dividend;
import com.stockplatform.mapper.DividendMapper;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DividendService {

    private final DividendMapper dividendMapper;

    public DividendService(DividendMapper dividendMapper) {
        this.dividendMapper = dividendMapper;
    }

    public DividendResponseDTO createDividend(DividendCreateDTO dto) {
        Dividend dividend = new Dividend();
        dividend.setAccountId(dto.getAccountId());
        dividend.setStockCode(dto.getStockCode());
        dividend.setStockName(dto.getStockName());
        dividend.setDividendAmount(dto.getDividendAmount());
        dividend.setDividendDate(dto.getDividendDate());
        dividend.setCreatedAt(LocalDateTime.now());
        dividendMapper.insertSelective(dividend);
        return DividendResponseDTO.fromEntity(dividend);
    }

    public List<DividendResponseDTO> listDividends(Integer accountId) {
        QueryCondition condition = QueryCondition.create();
        if (accountId != null) {
            condition.where("account_id = ?", accountId);
        }
        condition.orderBy("dividend_date", false);
        return dividendMapper.selectAllByCondition(condition).stream()
                .map(DividendResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}