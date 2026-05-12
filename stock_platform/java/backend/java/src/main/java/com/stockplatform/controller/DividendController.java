package com.stockplatform.controller;

import com.stockplatform.dto.DividendCreateDTO;
import com.stockplatform.dto.DividendResponseDTO;
import com.stockplatform.dto.PageDTO;
import com.stockplatform.service.DividendService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/dividends")
public class DividendController {

    private final DividendService dividendService;

    public DividendController(DividendService dividendService) {
        this.dividendService = dividendService;
    }

    @PostMapping
    public DividendResponseDTO createDividend(@Valid @RequestBody DividendCreateDTO dto) {
        return dividendService.createDividend(dto);
    }

    @GetMapping
    public PageDTO<DividendResponseDTO> listDividends(
            @RequestParam(required = false) Integer accountId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int perPage) {
        List<DividendResponseDTO> allDividends = dividendService.listDividends(accountId);
        return buildPageResponse(allDividends, page, perPage);
    }

    private PageDTO<DividendResponseDTO> buildPageResponse(List<DividendResponseDTO> allItems, int page, int perPage) {
        PageDTO<DividendResponseDTO> response = new PageDTO<>();
        int total = allItems.size();
        int start = (page - 1) * perPage;
        int end = Math.min(start + perPage, total);

        List<DividendResponseDTO> pageItems = start < total
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