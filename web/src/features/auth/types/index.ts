export type User = {
  id: string;
  name: string;
  email: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  token: string;
  user: User;
};
