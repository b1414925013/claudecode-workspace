package com.stockplatform.mapper;

import com.stockplatform.entity.Trade;
import com.mybatis-flex.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface TradeMapper extends BaseMapper<Trade> {
}