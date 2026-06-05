package com.stockplatform.dto;

import lombok.Data;
import java.util.List;

@Data
public class PageDTO<T> {
    private List<T> items;
    private PageMeta meta;

    @Data
    public static class PageMeta {
        private long total;
        private int page;
        private int perPage;
        private int pages;
        private boolean hasNext;
        private boolean hasPrev;
    }
}