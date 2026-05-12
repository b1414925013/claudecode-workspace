package com.stockplatform.mapper;

import com.stockplatform.entity.StockPrice;
import com.mybatis-flex.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface StockPriceMapper extends BaseMapper<StockPrice> {
}