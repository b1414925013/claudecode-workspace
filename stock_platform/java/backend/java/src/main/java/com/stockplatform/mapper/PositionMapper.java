package com.stockplatform.mapper;

import com.stockplatform.entity.Position;
import com.mybatis-flex.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PositionMapper extends BaseMapper<Position> {
}