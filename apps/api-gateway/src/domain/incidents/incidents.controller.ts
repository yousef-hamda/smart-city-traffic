import { Controller, Get, Query, UseGuards } from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { JwtAuthGuard } from "../../auth/guards/jwt-auth.guard";
import { Roles } from "../../rbac/roles.decorator";
import { RolesGuard } from "../../rbac/roles.guard";
import { IncidentsService } from "./incidents.service";
import { PaginationQueryDto, PaginatedResponseDto } from "../dto/pagination.dto";
import type { IncidentDto } from "../dto/incident.dto";

@ApiTags("incidents")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Controller("api/v1/incidents")
export class IncidentsController {
  constructor(private readonly incidentsService: IncidentsService) {}

  @Get()
  @Roles("admin", "analyst", "viewer")
  @ApiOperation({ summary: "List incidents" })
  findAll(@Query() pagination: PaginationQueryDto): Promise<PaginatedResponseDto<IncidentDto>> {
    return this.incidentsService.findAll(pagination);
  }
}
