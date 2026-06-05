package com.stockplatform.controller;

import com.stockplatform.dto.PageDTO;
import com.stockplatform.dto.TradeCreateDTO;
import com.stockplatform.dto.TradeResponseDTO;
import com.stockplatform.service.TradeService;
import jakarta.validation.Valid;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/trades")
public class TradeController {

    private final TradeService tradeService;

    public TradeController(TradeService tradeService) {
        this.tradeService = tradeService;
    }

    @PostMapping
    public TradeResponseDTO createTrade(@Valid @RequestBody TradeCreateDTO dto) {
        return tradeService.createTrade(dto);
    }

    @GetMapping
    public PageDTO<TradeResponseDTO> listTrades(
            @RequestParam(required = false) Integer accountId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int perPage) {
        List<TradeResponseDTO> allTrades = tradeService.listTrades(accountId, startDate, endDate);
        return buildPageResponse(allTrades, page, perPage);
    }

    private PageDTO<TradeResponseDTO> buildPageResponse(List<TradeResponseDTO> allItems, int page, int perPage) {
        PageDTO<TradeResponseDTO> response = new PageDTO<>();
        int total = allItems.size();
        int start = (page - 1) * perPage;
        int end = Math.min(start + perPage, total);

        List<TradeResponseDTO> pageItems = start < total
                ? allItems.subList(start, end)
                : List.of();

        PageDTO.PageMeta meta = new PageDTO.PageMeta();
        meta.setTotal(total);
        meta.setPage(page);
        meta.setPerPage(perPage);
        meta.setPages(total > 0 ? (int) Math.ceil((double) total / perPage) : 0);
        meta.setHasNext(page * perPage < total);
        meta.setHasPrev(page > 1);

        response.setItems(pageItems);
        response.setMeta(meta);
        return response;
    }
}