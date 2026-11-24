
import { describe, it, expect } from "vitest";

import { formatCurrency } from "./formatCurrency";

describe("formatCurrency", () => {

  it("formats an amount in Indian Rupees", () => {

    const result = formatCurrency(1000);

    expect(result).toContain("1,000");
    expect(result).toContain("₹");

  });

  it("formats zero correctly", () => {

    const result = formatCurrency(0);

    expect(result).toContain("0");

  });

});
