package com.stockplatform.dto;

import com.stockplatform.entity.Account;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class AccountResponseDTO {
    private Integer id;
    private String name;
    private String accountType;
    private LocalDateTime createdAt;

    public static AccountResponseDTO fromEntity(Account account) {
        AccountResponseDTO dto = new AccountResponseDTO();
        dto.setId(account.getId());
        dto.setName(account.getName());
        dto.setAccountType(account.getAccountType());
        dto.setCreatedAt(account.getCreatedAt());
        return dto;
    }
}