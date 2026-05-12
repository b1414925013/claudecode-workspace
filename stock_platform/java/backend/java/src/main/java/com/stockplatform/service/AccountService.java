package com.stockplatform.service;

import com.stockplatform.dto.AccountCreateDTO;
import com.stockplatform.dto.AccountResponseDTO;
import com.stockplatform.entity.Account;
import com.stockplatform.mapper.AccountMapper;
import com.my.mybatis.flex.core.Utils;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class AccountService {

    private final AccountMapper accountMapper;

    public AccountService(AccountMapper accountMapper) {
        this.accountMapper = accountMapper;
    }

    public List<AccountResponseDTO> getAllAccounts() {
        return accountMapper.selectAll().stream()
                .map(AccountResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    public AccountResponseDTO getAccountById(Integer id) {
        Account account = accountMapper.selectOneById(id);
        if (account == null) {
            throw new RuntimeException("账户不存在");
        }
        return AccountResponseDTO.fromEntity(account);
    }

    public AccountResponseDTO createAccount(AccountCreateDTO dto) {
        Account account = new Account();
        account.setName(dto.getName());
        account.setAccountType(dto.getAccountType() != null ? dto.getAccountType() : "cash");
        account.setCreatedAt(LocalDateTime.now());
        accountMapper.insertSelective(account);
        return AccountResponseDTO.fromEntity(account);
    }

    public void deleteAccount(Integer id) {
        accountMapper.deleteById(id);
    }

    public long getAccountCount() {
        return accountMapper.selectCount(null);
    }
}