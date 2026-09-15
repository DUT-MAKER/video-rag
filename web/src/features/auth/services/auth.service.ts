import { api } from "@/lib/api";
import type { LoginPayload, LoginResponse } from "../types";

export const authService = {
  login(payload: LoginPayload) {
    return api
      .post<LoginResponse>("/auth/login", payload)
      .then((response) => response.data);
  },
};
