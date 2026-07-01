import express from "express";
import { User } from "./models/User";

/**
 * Authentication middleware
 */
export function authenticate(req, res, next) {
  const token = req.headers.authorization;
  if (!token) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  next();
}

export class AuthService {
  constructor(userModel) {
    this.userModel = userModel;
  }

  async login(email, password) {
    const user = await this.userModel.findByEmail(email);
    if (!user) {
      throw new Error("User not found");
    }
    return { token: "jwt-token-here" };
  }
}

export default authenticate;