/**
 * HU.js - Hutool 风格的轻量前端工具库
 *
 * 纯原生 JavaScript 实现，零依赖，可直接 ``<script src="xxxxx.js"></script>`` 引入。
 * 挂载到全局 ``window.HU``，提供以下子模块：
 *   - HU.type     类型判断
 *   - HU.str      字符串工具
 *   - HU.array    数组工具
 *   - HU.object   对象工具
 *   - HU.num      数字工具
 *   - HU.date     日期工具
 *   - HU.func     函数工具（防抖/节流/记忆化）
 *   - HU.dom      DOM 操作
 *   - HU.storage  localStorage 封装
 *   - HU.http     fetch 封装
 *   - HU.url      URL 解析
 *
 * 同时支持 CommonJS（``module.exports``）与 ES Module（``export``）环境。
 */
(function (root, factory) {
  "use strict";

  if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = factory();
  } else if (typeof define === "function" && define.amd) {
    define([], factory);
  } else {
    root.HU = factory();
  }
})(typeof window !== "undefined" ? window : this, function () {
  "use strict";

  var HU = {};

  // ====================================================================
  // TypeUtil - 类型判断
  // ====================================================================
  var type = {};

  /**
   * 判断值是否为 null
   * @param {*} v 任意值
   * @returns {boolean}
   */
  type.isNull = function (v) {
    return v === null;
  };

  /**
   * 判断值是否为 undefined
   * @param {*} v
   * @returns {boolean}
   */
  type.isUndefined = function (v) {
    return typeof v === "undefined";
  };

  /**
   * 判断 null 或 undefined
   * @param {*} v
   * @returns {boolean}
   */
  type.isNil = function (v) {
    return v == null;
  };

  /**
   * 判断字符串
   * @param {*} v
   * @returns {boolean}
   */
  type.isString = function (v) {
    return typeof v === "string";
  };

  /**
   * 判断数字（含 NaN 返回 false）
   * @param {*} v
   * @returns {boolean}
   */
  type.isNumber = function (v) {
    return typeof v === "number" && !isNaN(v);
  };

  /**
   * 判断布尔
   * @param {*} v
   * @returns {boolean}
   */
  type.isBoolean = function (v) {
    return typeof v === "boolean";
  };

  /**
   * 判断函数
   * @param {*} v
   * @returns {boolean}
   */
  type.isFunction = function (v) {
    return typeof v === "function";
  };

  /**
   * 判断数组
   * @param {*} v
   * @returns {boolean}
   */
  type.isArray = function (v) {
    return Array.isArray(v);
  };

  /**
   * 判断 Date 实例
   * @param {*} v
   * @returns {boolean}
   */
  type.isDate = function (v) {
    return v instanceof Date && !isNaN(v.getTime());
  };

  /**
   * 判断 RegExp 实例
   * @param {*} v
   * @returns {boolean}
   */
  type.isRegExp = function (v) {
    return v instanceof RegExp;
  };

  /**
   * 判断纯对象（{} 或 new Object）
   * @param {*} v
   * @returns {boolean}
   */
  type.isPlainObject = function (v) {
    return Object.prototype.toString.call(v) === "[object Object]";
  };

  /**
   * 判断空值（null/undefined/空字符串/空数组/空对象）
   * @param {*} v
   * @returns {boolean}
   */
  type.isEmpty = function (v) {
    if (v == null) return true;
    if (type.isString(v) || type.isArray(v)) return v.length === 0;
    if (type.isPlainObject(v)) return Object.keys(v).length === 0;
    return false;
  };

  HU.type = type;

  // ====================================================================
  // StrUtil - 字符串工具
  // ====================================================================
  var str = {};

  /**
   * 判断空白字符串（null/undefined/全空格）
   * @param {*} s
   * @returns {boolean}
   */
  str.isBlank = function (s) {
    if (s == null) return true;
    if (typeof s !== "string") return false;
    return s.trim().length === 0;
  };

  /**
   * 判断非空白字符串
   * @param {*} s
   * @returns {boolean}
   */
  str.isNotBlank = function (s) {
    return !str.isBlank(s);
  };

  /**
   * 去除首尾空白；null/undefined 返回空字符串
   * @param {*} s
   * @returns {string}
   */
  str.trim = function (s) {
    return s == null ? "" : String(s).trim();
  };

  /**
   * 字符串格式化，``{0}``/``{name}`` 占位符
   * @param {string} template
   * @param {...*} args
   * @returns {string}
   */
  str.format = function (template) {
    var args = arguments;
    if (args.length === 2 && type.isPlainObject(args[1])) {
      // 命名占位符 {name}
      var ctx = args[1];
      return String(template).replace(/\{(\w+)\}/g, function (_, k) {
        return ctx.hasOwnProperty(k) ? String(ctx[k]) : "";
      });
    }
    // 索引占位符 {0} {1}
    return String(template).replace(/\{(\d+)\}/g, function (_, i) {
      var idx = parseInt(i, 10);
      return idx + 1 < args.length ? String(args[idx + 1]) : "";
    });
  };

  /**
   * 驼峰转下划线：``camelCase`` -> ``camel_case``
   * @param {string} s
   * @returns {string}
   */
  str.toUnderlineCase = function (s) {
    return String(s || "")
      .replace(/([A-Z])/g, "_$1")
      .replace(/^_/, "")
      .toLowerCase();
  };

  /**
   * 下划线转驼峰：``camel_case`` -> ``camelCase``
   * @param {string} s
   * @returns {string}
   */
  str.toCamelCase = function (s) {
    return String(s || "").replace(/_([a-z])/g, function (_, c) {
      return c.toUpperCase();
    });
  };

  /**
   * 左填充字符到指定长度
   * @param {string} s
   * @param {number} len 目标长度
   * @param {string} [char=" "] 填充字符
   * @returns {string}
   */
  str.padLeft = function (s, len, char) {
    s = String(s == null ? "" : s);
    char = char || " ";
    while (s.length < len) s = char + s;
    return s;
  };

  /**
   * 右填充字符到指定长度
   * @param {string} s
   * @param {number} len
   * @param {string} [char=" "]
   * @returns {string}
   */
  str.padRight = function (s, len, char) {
    s = String(s == null ? "" : s);
    char = char || " ";
    while (s.length < len) s = s + char;
    return s;
  };

  /**
   * HTML 转义（& < > " '）
   * @param {string} s
   * @returns {string}
   */
  str.escapeHtml = function (s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  };

  /**
   * HTML 反转义
   * @param {string} s
   * @returns {string}
   */
  str.unescapeHtml = function (s) {
    return String(s == null ? "" : s)
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'");
  };

  /**
   * 生成 UUID v4
   * @returns {string}
   */
  str.uuid = function () {
    if (typeof crypto !== "undefined" && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  /**
   * 截断字符串并加省略号
   * @param {string} s
   * @param {number} maxLen
   * @param {string} [suffix="..."]
   * @returns {string}
   */
  str.truncate = function (s, maxLen, suffix) {
    s = String(s == null ? "" : s);
    if (s.length <= maxLen) return s;
    return s.slice(0, maxLen) + (suffix || "...");
  };

  HU.str = str;

  // ====================================================================
  // ArrayUtil - 数组工具
  // ====================================================================
  var array = {};

  /**
   * 判断空数组或非数组
   * @param {*} v
   * @returns {boolean}
   */
  array.isEmpty = function (v) {
    return !type.isArray(v) || v.length === 0;
  };

  /**
   * 判断非空数组
   * @param {*} v
   * @returns {boolean}
   */
  array.isNotEmpty = function (v) {
    return !array.isEmpty(v);
  };

  /**
   * 数组去重（基于 Set）
   * @param {Array} arr
   * @returns {Array}
   */
  array.unique = function (arr) {
    if (!type.isArray(arr)) return [];
    return Array.from(new Set(arr));
  };

  /**
   * 按 key 去重对象数组
   * @param {Array} arr
   * @param {string} key
   * @returns {Array}
   */
  array.uniqueBy = function (arr, key) {
    if (!type.isArray(arr)) return [];
    var seen = new Set();
    var result = [];
    arr.forEach(function (item) {
      var k = item == null ? null : item[key];
      if (!seen.has(k)) {
        seen.add(k);
        result.push(item);
      }
    });
    return result;
  };

  /**
   * 数组扁平化（递归展开）
   * @param {Array} arr
   * @returns {Array}
   */
  array.flatten = function (arr) {
    if (!type.isArray(arr)) return [];
    var result = [];
    arr.forEach(function (item) {
      if (type.isArray(item)) {
        result = result.concat(array.flatten(item));
      } else {
        result.push(item);
      }
    });
    return result;
  };

  /**
   * 数组分块
   * @param {Array} arr
   * @param {number} size
   * @returns {Array[]}
   */
  array.chunk = function (arr, size) {
    if (!type.isArray(arr) || size <= 0) return [];
    var result = [];
    for (var i = 0; i < arr.length; i += size) {
      result.push(arr.slice(i, i + size));
    }
    return result;
  };

  /**
   * Fisher-Yates 洗牌算法
   * @param {Array} arr
   * @returns {Array} 打乱后的新数组（不改原数组）
   */
  array.shuffle = function (arr) {
    if (!type.isArray(arr)) return [];
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
    }
    return a;
  };

  /**
   * 生成数字范围数组
   * @param {number} start 起始值（含）
   * @param {number} end 结束值（不含）
   * @param {number} [step=1] 步长
   * @returns {number[]}
   */
  array.range = function (start, end, step) {
    step = step || 1;
    if (step === 0) return [];
    var result = [];
    if (step > 0) {
      for (var i = start; i < end; i += step) result.push(i);
    } else {
      for (var j = start; j > end; j += step) result.push(j);
    }
    return result;
  };

  /**
   * 数组按 key 分组
   * @param {Array} arr
   * @param {string|Function} key 字段名或取值函数
   * @returns {Object}
   */
  array.groupBy = function (arr, key) {
    if (!type.isArray(arr)) return {};
    var getter = type.isFunction(key) ? key : function (item) { return item[key]; };
    var result = {};
    arr.forEach(function (item) {
      var k = getter(item);
      if (!result[k]) result[k] = [];
      result[k].push(item);
    });
    return result;
  };

  HU.array = array;

  // ====================================================================
  // ObjectUtil - 对象工具
  // ====================================================================
  var object = {};

  /**
   * 深拷贝（基于 JSON，不支持函数/undefined/循环引用）
   * @param {*} obj
   * @returns {*}
   */
  object.deepClone = function (obj) {
    if (obj == null) return obj;
    return JSON.parse(JSON.stringify(obj));
  };

  /**
   * 深合并：把 sources 合并到 target，返回 target
   * @param {Object} target
   * @param {...Object} sources
   * @returns {Object}
   */
  object.merge = function (target) {
    if (!type.isPlainObject(target)) target = {};
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (!type.isPlainObject(src)) continue;
      for (var key in src) {
        if (!src.hasOwnProperty(key)) continue;
        if (type.isPlainObject(src[key]) && type.isPlainObject(target[key])) {
          target[key] = object.merge(target[key], src[key]);
        } else {
          target[key] = src[key];
        }
      }
    }
    return target;
  };

  /**
   * 从对象中挑选指定 key 组成新对象
   * @param {Object} obj
   * @param {string[]} keys
   * @returns {Object}
   */
  object.pick = function (obj, keys) {
    var result = {};
    if (!type.isPlainObject(obj)) return result;
    keys.forEach(function (k) {
      if (obj.hasOwnProperty(k)) result[k] = obj[k];
    });
    return result;
  };

  /**
   * 排除指定 key 组成新对象
   * @param {Object} obj
   * @param {string[]} keys
   * @returns {Object}
   */
  object.omit = function (obj, keys) {
    var result = {};
    if (!type.isPlainObject(obj)) return result;
    var exclude = new Set(keys || []);
    for (var k in obj) {
      if (obj.hasOwnProperty(k) && !exclude.has(k)) {
        result[k] = obj[k];
      }
    }
    return result;
  };

  /**
   * 安全读取嵌套属性（a.b.c 形式）
   * @param {Object} obj
   * @param {string} path
   * @param {*} [defaultVal]
   * @returns {*}
   */
  object.get = function (obj, path, defaultVal) {
    if (obj == null) return defaultVal;
    var parts = String(path).split(".");
    var cur = obj;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return defaultVal;
      cur = cur[parts[i]];
    }
    return cur == null ? defaultVal : cur;
  };

  HU.object = object;

  // ====================================================================
  // NumberUtil - 数字工具
  // ====================================================================
  var num = {};

  /**
   * 四舍五入到指定小数位
   * @param {number} n
   * @param {number} [precision=0]
   * @returns {number}
   */
  num.round = function (n, precision) {
    precision = precision || 0;
    var p = Math.pow(10, precision);
    return Math.round(n * p) / p;
  };

  /**
   * 生成 [min, max) 范围随机数
   * @param {number} min
   * @param {number} max
   * @returns {number}
   */
  num.random = function (min, max) {
    return Math.random() * (max - min) + min;
  };

  /**
   * 生成 [min, max] 范围随机整数
   * @param {number} min
   * @param {number} max
   * @returns {number}
   */
  num.randomInt = function (min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  };

  /**
   * 数字千分位格式化
   * @param {number} n
   * @param {number} [precision] 小数位
   * @returns {string}
   */
  num.format = function (n, precision) {
    if (isNaN(n)) return "";
    var fixed = precision != null ? n.toFixed(precision) : String(n);
    var parts = fixed.split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
  };

  /**
   * 判断整数
   * @param {*} v
   * @returns {boolean}
   */
  num.isInt = function (v) {
    return type.isNumber(v) && v % 1 === 0;
  };

  /**
   * 判断浮点数
   * @param {*} v
   * @returns {boolean}
   */
  num.isFloat = function (v) {
    return type.isNumber(v) && v % 1 !== 0;
  };

  HU.num = num;

  // ====================================================================
  // DateUtil - 日期工具
  // ====================================================================
  var date = {};

  // 日期格式化 token 对照表
  var DATE_FORMATTERS = {
    yyyy: function (d) { return d.getFullYear(); },
    MM: function (d) { return str.padLeft(d.getMonth() + 1, 2, "0"); },
    dd: function (d) { return str.padLeft(d.getDate(), 2, "0"); },
    HH: function (d) { return str.padLeft(d.getHours(), 2, "0"); },
    mm: function (d) { return str.padLeft(d.getMinutes(), 2, "0"); },
    ss: function (d) { return str.padLeft(d.getSeconds(), 2, "0"); },
  };

  /**
   * 日期格式化
   * @param {Date|string|number} d
   * @param {string} pattern 支持 yyyy/MM/dd HH:mm:ss
   * @returns {string}
   */
  date.format = function (d, pattern) {
    var dt = type.isDate(d) ? d : new Date(d);
    if (isNaN(dt.getTime())) return "";
    pattern = pattern || "yyyy-MM-dd HH:mm:ss";
    return pattern.replace(/(yyyy|MM|dd|HH|mm|ss)/g, function (tok) {
      return DATE_FORMATTERS[tok](dt);
    });
  };

  /**
   * 解析日期字符串（自动识别 ISO / yyyy-MM-dd HH:mm:ss 等）
   * @param {string} s
   * @returns {Date}
   */
  date.parse = function (s) {
    var d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
  };

  /**
   * 当前 Unix 时间戳（秒）
   * @returns {number}
   */
  date.now = function () {
    return Math.floor(Date.now() / 1000);
  };

  /**
   * 在日期上增加天数
   * @param {Date} d
   * @param {number} days
   * @returns {Date} 新日期对象
   */
  date.addDays = function (d, days) {
    var r = new Date(d.getTime());
    r.setDate(r.getDate() + days);
    return r;
  };

  /**
   * 在日期上增加月数（自动处理月底）
   * @param {Date} d
   * @param {number} months
   * @returns {Date}
   */
  date.addMonths = function (d, months) {
    var r = new Date(d.getTime());
    var targetMonth = r.getMonth() + months;
    r.setMonth(targetMonth);
    return r;
  };

  /**
   * 计算两个日期相差天数（绝对值）
   * @param {Date} d1
   * @param {Date} d2
   * @returns {number}
   */
  date.diffDays = function (d1, d2) {
    var ms = Math.abs(d1.getTime() - d2.getTime());
    return Math.floor(ms / (24 * 60 * 60 * 1000));
  };

  HU.date = date;

  // ====================================================================
  // FunctionUtil - 函数工具
  // ====================================================================
  var func = {};

  /**
   * 防抖：在 wait 毫秒内只执行最后一次
   * @param {Function} fn
   * @param {number} wait
   * @param {boolean} [immediate=false] 是否立即执行首次
   * @returns {Function}
   */
  func.debounce = function (fn, wait, immediate) {
    var timer = null;
    return function () {
      var ctx = this;
      var args = arguments;
      if (timer) clearTimeout(timer);
      if (immediate && !timer) {
        fn.apply(ctx, args);
      }
      timer = setTimeout(function () {
        timer = null;
        if (!immediate) fn.apply(ctx, args);
      }, wait);
    };
  };

  /**
   * 节流：在 wait 毫秒内最多执行一次
   * @param {Function} fn
   * @param {number} wait
   * @returns {Function}
   */
  func.throttle = function (fn, wait) {
    var last = 0;
    var timer = null;
    return function () {
      var ctx = this;
      var args = arguments;
      var now = Date.now();
      var remain = wait - (now - last);
      if (remain <= 0) {
        if (timer) { clearTimeout(timer); timer = null; }
        last = now;
        fn.apply(ctx, args);
      } else if (!timer) {
        timer = setTimeout(function () {
          last = Date.now();
          timer = null;
          fn.apply(ctx, args);
        }, remain);
      }
    };
  };

  /**
   * 只执行一次的函数
   * @param {Function} fn
   * @returns {Function}
   */
  func.once = function (fn) {
    var called = false;
    var result;
    return function () {
      if (called) return result;
      called = true;
      result = fn.apply(this, arguments);
      return result;
    };
  };

  /**
   * 记忆化：缓存函数返回值
   * @param {Function} fn
   * @returns {Function}
   */
  func.memoize = function (fn) {
    var cache = new Map();
    return function () {
      var key = JSON.stringify(arguments);
      if (cache.has(key)) return cache.get(key);
      var r = fn.apply(this, arguments);
      cache.set(key, r);
      return r;
    };
  };

  HU.func = func;

  // ====================================================================
  // DomUtil - DOM 操作
  // ====================================================================
  var dom = {};

  /**
   * querySelector 简写
   * @param {string} selector
   * @param {Element} [parent=document]
   * @returns {Element|null}
   */
  dom.$ = function (selector, parent) {
    return (parent || document).querySelector(selector);
  };

  /**
   * querySelectorAll 简写，返回数组
   * @param {string} selector
   * @param {Element} [parent=document]
   * @returns {Element[]}
   */
  dom.$$ = function (selector, parent) {
    return Array.from((parent || document).querySelectorAll(selector));
  };

  /**
   * 绑定事件
   * @param {Element} el
   * @param {string} event
   * @param {Function} handler
   * @returns {Function} 解绑函数
   */
  dom.on = function (el, event, handler) {
    el.addEventListener(event, handler);
    return function () { el.removeEventListener(event, handler); };
  };

  /**
   * 添加 class
   * @param {Element} el
   * @param {string} cls
   */
  dom.addClass = function (el, cls) {
    if (el && el.classList) el.classList.add(cls);
  };

  /**
   * 移除 class
   * @param {Element} el
   * @param {string} cls
   */
  dom.removeClass = function (el, cls) {
    if (el && el.classList) el.classList.remove(cls);
  };

  /**
   * 判断是否包含 class
   * @param {Element} el
   * @param {string} cls
   * @returns {boolean}
   */
  dom.hasClass = function (el, cls) {
    return !!(el && el.classList && el.classList.contains(cls));
  };

  /**
   * 切换 class
   * @param {Element} el
   * @param {string} cls
   */
  dom.toggleClass = function (el, cls) {
    if (el && el.classList) el.classList.toggle(cls);
  };

  /**
   * 批量设置样式
   * @param {Element} el
   * @param {Object} props
   */
  dom.css = function (el, props) {
    if (!el) return;
    Object.keys(props).forEach(function (k) {
      el.style[k] = props[k];
    });
  };

  /**
   * 设置/获取属性
   * @param {Element} el
   * @param {string} name
   * @param {string} [val]
   * @returns {string|undefined}
   */
  dom.attr = function (el, name, val) {
    if (val === undefined) return el ? el.getAttribute(name) : null;
    if (el) el.setAttribute(name, val);
  };

  HU.dom = dom;

  // ====================================================================
  // StorageUtil - localStorage 封装
  // ====================================================================
  var storage = {};

  /**
   * 存储 JSON 值
   * @param {string} key
   * @param {*} value
   */
  storage.set = function (key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.error("[HU.storage.set]", e);
    }
  };

  /**
   * 读取 JSON 值，失败返回 defaultVal
   * @param {string} key
   * @param {*} [defaultVal]
   * @returns {*}
   */
  storage.get = function (key, defaultVal) {
    try {
      var raw = localStorage.getItem(key);
      return raw == null ? defaultVal : JSON.parse(raw);
    } catch (e) {
      return defaultVal;
    }
  };

  /**
   * 移除指定 key
   * @param {string} key
   */
  storage.remove = function (key) {
    localStorage.removeItem(key);
  };

  /**
   * 清空全部
   */
  storage.clear = function () {
    localStorage.clear();
  };

  HU.storage = storage;

  // ====================================================================
  // HttpUtil - fetch 封装
  // ====================================================================
  var http = {};

  /**
   * 默认配置
   */
  http.defaults = {
    baseUrl: "",
    timeout: 30000,
    headers: { "Content-Type": "application/json" },
  };

  /**
   * 发起 fetch 请求
   * @param {string} method HTTP 方法
   * @param {string} url
   * @param {Object} [options] { params, body, headers, timeout }
   * @returns {Promise<Object>}
   */
  function _request(method, url, options) {
    options = options || {};
    var fullUrl = (http.defaults.baseUrl || "") + url;

    // query 参数拼接
    if (options.params) {
      var qs = Object.keys(options.params)
        .map(function (k) {
          return encodeURIComponent(k) + "=" + encodeURIComponent(options.params[k]);
        })
        .join("&");
      if (qs) fullUrl += (fullUrl.indexOf("?") >= 0 ? "&" : "?") + qs;
    }

    var headers = Object.assign({}, http.defaults.headers, options.headers || {});
    var fetchOpts = { method: method, headers: headers };
    if (options.body && method !== "GET" && method !== "HEAD") {
      fetchOpts.body = typeof options.body === "string"
        ? options.body
        : JSON.stringify(options.body);
    }

    var timer = null;
    var promise = fetch(fullUrl, fetchOpts).then(function (resp) {
      if (!resp.ok) {
        var err = new Error("HTTP " + resp.status + " " + resp.statusText);
        err.status = resp.status;
        err.response = resp;
        throw err;
      }
      var ct = resp.headers.get("Content-Type") || "";
      if (ct.indexOf("application/json") >= 0) return resp.json();
      return resp.text();
    });

    var timeout = options.timeout != null ? options.timeout : http.defaults.timeout;
    if (timeout > 0) {
      return new Promise(function (resolve, reject) {
        timer = setTimeout(function () {
          reject(new Error("timeout after " + timeout + "ms"));
        }, timeout);
        promise.then(
          function (v) { clearTimeout(timer); resolve(v); },
          function (e) { clearTimeout(timer); reject(e); }
        );
      });
    }
    return promise;
  }

  /**
   * GET 请求
   */
  http.get = function (url, options) { return _request("GET", url, options); };
  /**
   * POST 请求
   */
  http.post = function (url, body, options) {
    var o = Object.assign({}, options || {});
    o.body = body;
    return _request("POST", url, o);
  };
  /**
   * PUT 请求
   */
  http.put = function (url, body, options) {
    var o = Object.assign({}, options || {});
    o.body = body;
    return _request("PUT", url, o);
  };
  /**
   * DELETE 请求
   */
  http.delete = function (url, options) { return _request("DELETE", url, options); };

  HU.http = http;

  // ====================================================================
  // UrlUtil - URL 解析工具
  // ====================================================================
  var url = {};

  /**
   * 解析 URL，返回 { protocol, host, pathname, search, hash, params }
   * @param {string} u
   * @returns {Object}
   */
  url.parse = function (u) {
    var a = document.createElement("a");
    a.href = u;
    var params = {};
    if (a.search) {
      a.search.slice(1).split("&").forEach(function (kv) {
        var i = kv.indexOf("=");
        if (i > 0) {
          params[decodeURIComponent(kv.slice(0, i))] = decodeURIComponent(kv.slice(i + 1));
        }
      });
    }
    return {
      protocol: a.protocol,
      host: a.host,
      hostname: a.hostname,
      port: a.port,
      pathname: a.pathname,
      search: a.search,
      hash: a.hash,
      params: params,
    };
  };

  /**
   * 把 params 对象拼到 query string
   * @param {Object} params
   * @returns {string}
   */
  url.buildQuery = function (params) {
    return Object.keys(params || {})
      .map(function (k) {
        return encodeURIComponent(k) + "=" + encodeURIComponent(params[k]);
      })
      .join("&");
  };

  HU.url = url;

  // ====================================================================
  // CookieUtil - Cookie 操作
  // ====================================================================
  var cookie = {};

  /**
   * 设置 cookie
   * @param {string} name
   * @param {string} value
   * @param {Object} [opts] { expires, path, domain, secure }
   */
  cookie.set = function (name, value, opts) {
    opts = opts || {};
    var parts = [name + "=" + encodeURIComponent(value)];
    if (opts.expires) {
      var d = type.isDate(opts.expires) ? opts.expires : new Date(opts.expires);
      parts.push("expires=" + d.toUTCString());
    }
    if (opts.path) parts.push("path=" + opts.path);
    if (opts.domain) parts.push("domain=" + opts.domain);
    if (opts.secure) parts.push("secure");
    document.cookie = parts.join("; ");
  };

  /**
   * 读取 cookie
   * @param {string} name
   * @returns {string|null}
   */
  cookie.get = function (name) {
    var m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : null;
  };

  /**
   * 删除 cookie
   * @param {string} name
   * @param {string} [path]
   */
  cookie.remove = function (name, path) {
    cookie.set(name, "", { expires: new Date(0), path: path || "/" });
  };

  HU.cookie = cookie;

  // ====================================================================
  // EventUtil - 自定义事件总线
  // ====================================================================
  var event = (function () {
    var listeners = new Map();

    return {
      /**
       * 订阅事件
       * @param {string} name
       * @param {Function} handler
       * @returns {Function} 取消订阅函数
       */
      on: function (name, handler) {
        if (!listeners.has(name)) listeners.set(name, new Set());
        listeners.get(name).add(handler);
        return function () {
          var set = listeners.get(name);
          if (set) set.delete(handler);
        };
      },
      /**
       * 触发事件
       * @param {string} name
       * @param {*} [data]
       */
      emit: function (name, data) {
        var set = listeners.get(name);
        if (!set) return;
        set.forEach(function (h) {
          try { h(data); } catch (e) { console.error("[HU.event.emit]", e); }
        });
      },
      /**
       * 取消所有订阅
       * @param {string} [name] 不传则清空全部
       */
      off: function (name) {
        if (name) listeners.delete(name);
        else listeners.clear();
      },
    };
  })();

  HU.event = event;

  // ====================================================================
  // 工具导出
  // ====================================================================
  HU.version = "0.1.0";

  return HU;
});
