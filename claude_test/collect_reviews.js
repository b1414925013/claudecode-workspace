async page => {
  const allReviews = [];
  const seen = new Set();
  const filters = ['全部', '图/视频', '追评', '性价比高', '安装简单', '开机速度快', '物有所值', '配件齐全', '物超所值', '质量非常好'];

  for (const filter of filters) {
    await page.evaluate((f) => {
      const spans = document.querySelectorAll('[class*=imprItem]');
      for (const s of spans) {
        if (s.textContent.trim().startsWith(f)) {
          s.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
          return;
        }
      }
    }, filter);
    await page.waitForTimeout(1500);

    const reviews = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.Comment--H5QmJwe9')).map(el => {
        const userName = el.querySelector('[class*=userName]') ? el.querySelector('[class*=userName]').textContent.trim() : '';
        const meta = el.querySelector('[class*=meta]') ? el.querySelector('[class*=meta]').textContent.trim() : '';
        const content = el.querySelector('[class*=content--uonoOhaz]') ? (el.querySelector('[class*=content--uonoOhaz]').getAttribute('title') || el.querySelector('[class*=content--uonoOhaz]').textContent.trim()) : '';

        let append = '';
        const appendEl = el.querySelector('[class*=appendInternal]');
        if (appendEl) {
          append = appendEl.textContent.trim();
          const appendContent = el.querySelector('[class*=append] [class*=content--uonoOhaz]');
          if (appendContent) {
            appendContent.childNodes.forEach(n => {
              if (n.nodeType === 3 && n.textContent.trim()) append += ' ' + n.textContent.trim();
            });
          }
        }
        return { userName, meta, content, append };
      });
    });

    for (const r of reviews) {
      const key = r.content;
      if (!seen.has(key)) {
        seen.add(key);
        allReviews.push(r);
      }
    }
  }

  // Sort by date (newest first)
  allReviews.sort((a, b) => {
    const dateA = a.meta.match(/(\d{4})[年-](\d{1,2})[月-](\d{1,2})/);
    const dateB = b.meta.match(/(\d{4})[年-](\d{1,2})[月-](\d{1,2})/);
    if (dateA && dateB) {
      const ta = new Date(dateA[1], dateA[2]-1, dateA[3]);
      const tb = new Date(dateB[1], dateB[2]-1, dateB[3]);
      return tb - ta;
    }
    return 0;
  });

  // Return JSON data
  const top100 = allReviews.slice(0, 100).map(r => {
    const dateMatch = r.meta.match(/(\d{4})[年-](\d{1,2})[月-](\d{1,2})/);
    let dateStr = r.meta;
    let configStr = '';
    if (r.meta.includes('已购：')) {
      const idx = r.meta.indexOf('已购：');
      dateStr = r.meta.substring(0, idx).trim();
      configStr = r.meta.substring(idx);
    }
    return { userName: r.userName, date: dateStr, config: configStr, content: r.content, append: r.append };
  });

  return JSON.stringify({ count: top100.length, reviews: top100 });
}
