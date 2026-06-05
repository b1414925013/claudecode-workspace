package com.stockplatform.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AccountCreateDTO {

    @NotBlank(message = "账户名称不能为空")
    private String name;

    private String accountType = "cash";
}