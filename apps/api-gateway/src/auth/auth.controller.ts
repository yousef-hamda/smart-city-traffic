import {
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Request,
  UseGuards,
} from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { AuthService } from "./auth.service";
import { RegisterDto } from "./dto/register.dto";
import { LoginDto } from "./dto/login.dto";
import { AuthResponseDto } from "./dto/auth-response.dto";
import { JwtAuthGuard } from "./guards/jwt-auth.guard";
import type { AuthenticatedUser } from "./strategies/jwt.strategy";

interface RefreshBody {
  refreshToken: string;
}

interface AuthenticatedRequest {
  user: AuthenticatedUser;
}

@ApiTags("auth")
@Controller("api/v1/auth")
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post("register")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Register a new user" })
  async register(@Body() dto: RegisterDto): Promise<AuthResponseDto & { refreshToken: string }> {
    return this.authService.register(dto);
  }

  @Post("login")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Login with email and password" })
  async login(@Body() dto: LoginDto): Promise<AuthResponseDto & { refreshToken: string }> {
    return this.authService.login(dto);
  }

  @Post("refresh")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Refresh access token" })
  async refresh(@Body() body: RefreshBody): Promise<AuthResponseDto & { refreshToken: string }> {
    return this.authService.refresh(body.refreshToken);
  }

  @Post("logout")
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: "Logout (revoke refresh token)" })
  async logout(@Body() body: RefreshBody): Promise<void> {
    return this.authService.logout(body.refreshToken);
  }

  @Get("me")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: "Get current user profile" })
  async me(
    @Request() req: AuthenticatedRequest,
  ): Promise<{ id: string; email: string; role: string; locale: string; createdAt: Date }> {
    return this.authService.getMe(req.user.userId);
  }
}
