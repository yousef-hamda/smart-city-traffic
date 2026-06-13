import { Controller, Get, Query, UseGuards } from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { JwtAuthGuard } from "../../auth/guards/jwt-auth.guard";
import { AlertsService } from "./alerts.service";
import { PaginationQueryDto, PaginatedResponseDto } from "../dto/pagination.dto";
import type { AlertDto } from "../dto/alert.dto";

@ApiTags("alerts")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("api/v1/alerts")
export class AlertsController {
  constructor(private readonly alertsService: AlertsService) {}

  @Get()
  @ApiOperation({ summary: "List alerts" })
  findAll(@Query() pagination: PaginationQueryDto): Promise<PaginatedResponseDto<AlertDto>> {
    return this.alertsService.findAll(pagination);
  }
}
