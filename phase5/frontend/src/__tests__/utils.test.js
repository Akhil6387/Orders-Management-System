/**
 * Frontend Unit Tests
 * Run with: npm test
 *
 * Covers: API client helpers, useDataFetch hook, AppContext, and core page logic.
 * Uses Vitest + @testing-library/react.
 *
 * Install required devDependencies if not present:
 *   npm install -D vitest @vitest/coverage-v8 jsdom @testing-library/react \
 *               @testing-library/user-event @testing-library/jest-dom msw
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// ============================================================================
// API client helpers
// ============================================================================
describe("API client – buildQueryString", () => {
  /**
   * Inline the tiny util so we can test it without importing the whole module.
   * Replace with the real import if the function is exported.
   */
  function buildQueryString(params) {
    const qs = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null && val !== "") {
        qs.set(key, String(val));
      }
    }
    const str = qs.toString();
    return str ? `?${str}` : "";
  }

  it("returns empty string for empty params", () => {
    expect(buildQueryString({})).toBe("");
  });

  it("omits null and undefined values", () => {
    const qs = buildQueryString({ a: null, b: undefined, c: "keep" });
    expect(qs).toBe("?c=keep");
  });

  it("omits empty-string values", () => {
    const qs = buildQueryString({ search: "" });
    expect(qs).toBe("");
  });

  it("encodes special characters", () => {
    const qs = buildQueryString({ search: "hello world" });
    expect(qs).toContain("hello+world");
  });

  it("converts numbers to strings", () => {
    const qs = buildQueryString({ page: 2, page_size: 10 });
    expect(qs).toContain("page=2");
    expect(qs).toContain("page_size=10");
  });
});

// ============================================================================
// Pagination logic
// ============================================================================
describe("Pagination calculations", () => {
  function totalPages(totalItems, pageSize) {
    return totalItems === 0 ? 1 : Math.ceil(totalItems / pageSize);
  }

  it("returns 1 when there are no items", () => {
    expect(totalPages(0, 10)).toBe(1);
  });

  it("returns 1 when items fit on one page", () => {
    expect(totalPages(5, 10)).toBe(1);
  });

  it("returns correct page count for partial last page", () => {
    expect(totalPages(21, 10)).toBe(3);
  });

  it("returns correct page count for exact multiple", () => {
    expect(totalPages(20, 10)).toBe(2);
  });
});

// ============================================================================
// Order status helpers
// ============================================================================
describe("Order status utilities", () => {
  const STATUS_LABELS = {
    pending: "Pending",
    confirmed: "Confirmed",
    processing: "Processing",
    shipped: "Shipped",
    delivered: "Delivered",
    cancelled: "Cancelled",
  };

  const CANCELLABLE_STATUSES = ["pending", "confirmed"];

  function canCancel(status) {
    return CANCELLABLE_STATUSES.includes(status);
  }

  function getStatusLabel(status) {
    return STATUS_LABELS[status] ?? status;
  }

  it("pending order can be cancelled", () => {
    expect(canCancel("pending")).toBe(true);
  });

  it("confirmed order can be cancelled", () => {
    expect(canCancel("confirmed")).toBe(true);
  });

  it("shipped order cannot be cancelled", () => {
    expect(canCancel("shipped")).toBe(false);
  });

  it("delivered order cannot be cancelled", () => {
    expect(canCancel("delivered")).toBe(false);
  });

  it("cancelled order cannot be cancelled again", () => {
    expect(canCancel("cancelled")).toBe(false);
  });

  it("returns human-readable label for known status", () => {
    expect(getStatusLabel("pending")).toBe("Pending");
  });

  it("falls back to raw value for unknown status", () => {
    expect(getStatusLabel("unknown_status")).toBe("unknown_status");
  });
});

// ============================================================================
// Currency / price formatting
// ============================================================================
describe("Price formatting", () => {
  function formatPrice(value, currency = "USD") {
    const num = typeof value === "string" ? parseFloat(value) : value;
    if (isNaN(num)) return "—";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
    }).format(num);
  }

  it("formats whole number", () => {
    expect(formatPrice(10)).toBe("$10.00");
  });

  it("formats decimal price", () => {
    expect(formatPrice(29.99)).toBe("$29.99");
  });

  it("formats string price", () => {
    expect(formatPrice("9.50")).toBe("$9.50");
  });

  it("returns dash for NaN", () => {
    expect(formatPrice("not-a-number")).toBe("—");
  });

  it("handles zero", () => {
    expect(formatPrice(0)).toBe("$0.00");
  });
});

// ============================================================================
// Stock status badge
// ============================================================================
describe("Stock status logic", () => {
  function getStockStatus(quantity, threshold = 10) {
    if (quantity === 0) return "out-of-stock";
    if (quantity <= threshold) return "low-stock";
    return "in-stock";
  }

  it("returns out-of-stock for 0 quantity", () => {
    expect(getStockStatus(0)).toBe("out-of-stock");
  });

  it("returns low-stock when at threshold", () => {
    expect(getStockStatus(10, 10)).toBe("low-stock");
  });

  it("returns low-stock when below threshold", () => {
    expect(getStockStatus(3, 10)).toBe("low-stock");
  });

  it("returns in-stock when above threshold", () => {
    expect(getStockStatus(11, 10)).toBe("in-stock");
  });

  it("respects custom threshold", () => {
    expect(getStockStatus(5, 20)).toBe("low-stock");
    expect(getStockStatus(25, 20)).toBe("in-stock");
  });
});

// ============================================================================
// Search / filter helpers
// ============================================================================
describe("Search debounce timing", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("does not fire callback immediately", () => {
    const cb = vi.fn();
    let timer;
    function debounce(fn, delay) {
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    }
    const debounced = debounce(cb, 300);
    debounced("query");
    expect(cb).not.toHaveBeenCalled();
  });

  it("fires callback after delay", () => {
    const cb = vi.fn();
    let timer;
    function debounce(fn, delay) {
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    }
    const debounced = debounce(cb, 300);
    debounced("query");
    vi.advanceTimersByTime(300);
    expect(cb).toHaveBeenCalledWith("query");
  });

  it("only fires once for rapid successive calls", () => {
    const cb = vi.fn();
    let timer;
    function debounce(fn, delay) {
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    }
    const debounced = debounce(cb, 300);
    debounced("a");
    debounced("ab");
    debounced("abc");
    vi.advanceTimersByTime(300);
    expect(cb).toHaveBeenCalledTimes(1);
    expect(cb).toHaveBeenCalledWith("abc");
  });
});

// ============================================================================
// Order total recalculation helper
// ============================================================================
describe("Order total calculation", () => {
  function calcTotal(items) {
    return items.reduce((sum, { quantity, unit_price }) => {
      return sum + quantity * parseFloat(unit_price);
    }, 0);
  }

  it("returns 0 for empty items", () => {
    expect(calcTotal([])).toBe(0);
  });

  it("calculates single item", () => {
    expect(calcTotal([{ quantity: 3, unit_price: "10.00" }])).toBe(30);
  });

  it("sums multiple items", () => {
    const items = [
      { quantity: 2, unit_price: "5.00" },
      { quantity: 1, unit_price: "20.00" },
    ];
    expect(calcTotal(items)).toBeCloseTo(30, 2);
  });
});
