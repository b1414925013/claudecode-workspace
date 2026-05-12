package com.stockplatform.entity;

import com.mybatis-flex.core.annotation.Id;
import com.mybatis-flex.core.annotation.Table;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Table("accounts")
public class Account {

    @Id
    private Integer id;

    private String name;

    private String accountType;

    private LocalDateTime createdAt;
}