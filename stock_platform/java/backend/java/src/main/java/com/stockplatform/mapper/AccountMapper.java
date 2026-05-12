package com.stockplatform.mapper;

import com.stockplatform.entity.Account;
import com.mybatis-flex.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface AccountMapper extends BaseMapper<Account> {
}