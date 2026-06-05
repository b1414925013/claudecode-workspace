package com.stockplatform.controller;

import com.stockplatform.dto.StatisticsDTO;
import com.stockplatform.dto.SummaryDTO;
import com.stockplatform.service.StatisticsService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api")
public class StatisticsController {

    private final StatisticsService statisticsService;

    public StatisticsController(StatisticsService statisticsService) {
        this.statisticsService = statisticsService;
    }

    @GetMapping("/statistics")
    public StatisticsDTO getStatistics(
            @RequestParam(required = false) Integer accountId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        return statisticsService.getStatistics(accountId, startDate, endDate);
    }

    @GetMapping("/summary")
    public SummaryDTO getSummary() {
        return statisticsService.getSummary();
    }
}