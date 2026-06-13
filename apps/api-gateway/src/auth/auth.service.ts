import {
  ConflictException,
  Injectable,
  NotFoundException,
  UnauthorizedException,
} from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import { ConfigService } from "@nestjs/config";
import * as argon2 from "argon2";
import * as crypto from "crypto";
import type { AppConfig } from "../config/configuration";
import { PrismaService } from "../prisma/prisma.service";
import type { RegisterDto } from "./dto/register.dto";
import type { LoginDto } from "./dto/login.dto";
import type { AuthResponseDto } from "./dto/auth-response.dto";
import type { JwtPayload } from "./entities/jwt-payload.entity";

interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

interface UserRecord {
  id: string;
  email: string;
  role: string;
}

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService<AppConfig>,
  ) {}

  async register(dto: RegisterDto): Promise<AuthResponseDto & { refreshToken: string }> {
    const existing = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException("Email already registered");
    }

    const passwordHash = await argon2.hash(dto.password);
    const id = crypto.randomUUID();

    const user = await this.prisma.user.create({
      data: { id, email: dto.email, passwordHash, role: "viewer" },
      select: { id: true, email: true, role: true },
    });

    const tokens = await this.issueTokens(user);
    return {
      accessToken: tokens.accessToken,
      tokenType: "Bearer",
      refreshToken: tokens.refreshToken,
    };
  }

  async login(dto: LoginDto): Promise<AuthResponseDto & { refreshToken: string }> {
    const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (!user) {
      throw new UnauthorizedException("Invalid credentials");
    }

    const valid = await argon2.verify(user.passwordHash, dto.password);
    if (!valid) {
      throw new UnauthorizedException("Invalid credentials");
    }

    const tokens = await this.issueTokens({ id: user.id, email: user.email, role: user.role });
    return {
      accessToken: tokens.accessToken,
      tokenType: "Bearer",
      refreshToken: tokens.refreshToken,
    };
  }

  async refresh(refreshToken: string): Promise<AuthResponseDto & { refreshToken: string }> {
    const tokenHash = crypto.createHash("sha256").update(refreshToken).digest("hex");

    const stored = await this.prisma.refreshToken.findFirst({
      where: { tokenHash, revoked: false },
      include: { user: { select: { id: true, email: true, role: true } } },
    });

    if (!stored || stored.expiresAt < new Date()) {
      throw new UnauthorizedException("Refresh token invalid or expired");
    }

    // Revoke the old token
    await this.prisma.refreshToken.update({
      where: { id: stored.id },
      data: { revoked: true },
    });

    const tokens = await this.issueTokens(stored.user);
    return {
      accessToken: tokens.accessToken,
      tokenType: "Bearer",
      refreshToken: tokens.refreshToken,
    };
  }

  async logout(refreshToken: string): Promise<void> {
    const tokenHash = crypto.createHash("sha256").update(refreshToken).digest("hex");
    await this.prisma.refreshToken.updateMany({
      where: { tokenHash },
      data: { revoked: true },
    });
  }

  async getMe(
    userId: string,
  ): Promise<{ id: string; email: string; role: string; locale: string; createdAt: Date }> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: { id: true, email: true, role: true, locale: true, createdAt: true },
    });
    if (!user) {
      throw new NotFoundException("User not found");
    }
    return user;
  }

  private async issueTokens(user: UserRecord): Promise<TokenPair> {
    const payload: JwtPayload = { sub: user.id, email: user.email, role: user.role };

    const accessTtl = this.config.get<number>("JWT_ACCESS_TTL") ?? 900;
    const refreshTtl = this.config.get<number>("JWT_REFRESH_TTL") ?? 604800;
    const refreshSecret = this.config.get<string>("JWT_REFRESH_SECRET") ?? "dev-refresh-secret";

    const accessToken = this.jwt.sign(payload, { expiresIn: accessTtl });
    const refreshTokenPlain = crypto.randomBytes(64).toString("hex");
    const tokenHash = crypto.createHash("sha256").update(refreshTokenPlain).digest("hex");

    const refreshId = crypto.randomUUID();
    await this.prisma.refreshToken.create({
      data: {
        id: refreshId,
        userId: user.id,
        tokenHash,
        expiresAt: new Date(Date.now() + refreshTtl * 1000),
        revoked: false,
      },
    });

    // Sign refresh token separately for verification
    const signedRefresh = this.jwt.sign(
      { sub: user.id, jti: refreshId },
      { secret: refreshSecret, expiresIn: refreshTtl },
    );

    // Return the plaintext random token (not the signed JWT) as the refresh token
    // The hash is stored in DB; clients send back this plaintext value
    void signedRefresh; // We store hash of refreshTokenPlain, not the JWT
    return { accessToken, refreshToken: refreshTokenPlain };
  }
}
