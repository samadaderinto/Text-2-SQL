import axios from "axios";
import { afterEach, describe, expect, it, vi } from "vitest";
import { reportClientError } from "../utils/error-reporting";

vi.mock("axios", () => ({
  default: { post: vi.fn().mockResolvedValue({}) },
}));

describe("client error reporting", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("redacts sensitive text and strips route query parameters", async () => {
    vi.useFakeTimers();

    reportClientError({
      level: "error",
      event_type: "api_error",
      message: "user@example.com failed with password=hunter2",
      route: "/orders?token=private",
      method: "get",
      status_code: 500,
    });

    await vi.advanceTimersByTimeAsync(500);

    const event = vi.mocked(axios.post).mock.calls[0][1] as {
      message: string;
      route: string;
    };
    expect(event.message).not.toContain("user@example.com");
    expect(event.message).not.toContain("hunter2");
    expect(event.route).toBe("/orders");
  });
});
