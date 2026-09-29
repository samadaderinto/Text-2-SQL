import { describe, expect, it } from "vitest";
import { getApiErrorMessage } from "../utils/api-errors";

describe("getApiErrorMessage", () => {
  it("extracts DRF validation messages", () => {
    const error = {
      response: {
        status: 400,
        data: { email: ["This email is already registered."] },
      },
      isAxiosError: true,
    };
    expect(getApiErrorMessage(error)).toBe(
      "email: This email is already registered.",
    );
  });

  it("does not expose server error response details", () => {
    const error = {
      response: { status: 500, data: { detail: "database password leaked" } },
      isAxiosError: true,
    };
    expect(getApiErrorMessage(error, "Could not save changes.")).toBe(
      "Could not save changes.",
    );
  });
});
