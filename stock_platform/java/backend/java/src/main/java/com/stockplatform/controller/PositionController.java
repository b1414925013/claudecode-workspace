package com.stockplatform.controller;

import com.stockplatform.dto.PageDTO;
import com.stockplatform.dto.PositionCreateDTO;
import com.stockplatform.dto.PositionResponseDTO;
import com.stockplatform.service.PositionService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/positions")
public class PositionController {

    private final PositionService positionService;

    public PositionController(PositionService positionService) {
        this.positionService = positionService;
    }

    @PostMapping
    public PositionResponseDTO createPosition(@Valid @RequestBody PositionCreateDTO dto) {
        return positionService.createPosition(dto);
    }

    @GetMapping
    public PageDTO<PositionResponseDTO> listPositions(
            @RequestParam(required = false) Integer accountId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int perPage) {
        List<PositionResponseDTO> allPositions = positionService.listPositions(accountId);
        return buildPageResponse(allPositions, page, perPage);
    }

    @GetMapping("/account/{accountId}")
    public List<PositionResponseDTO> listPositionsByAccount(@PathVariable Integer accountId) {
        return positionService.listPositionsByAccount(accountId);
    }

    @GetMapping("/{id}")
    public PositionResponseDTO getPosition(@PathVariable Integer id) {
        return positionService.getPosition(id);
    }

    @PutMapping("/{id}")
    public PositionResponseDTO updatePosition(@PathVariable Integer id, @Valid @RequestBody PositionCreateDTO dto) {
        return positionService.updatePosition(id, dto);
    }

    @DeleteMapping("/{id}")
    public void deletePosition(@PathVariable Integer id) {
        positionService.deletePosition(id);
    }

    private PageDTO<PositionResponseDTO> buildPageResponse(List<PositionResponseDTO> allItems, int page, int perPage) {
        PageDTO<PositionResponseDTO> response = new PageDTO<>();
        int total = allItems.size();
        int start = (page - 1) * perPage;
        int end = Math.min(start + perPage, total);

        List<PositionResponseDTO> pageItems = start < total
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