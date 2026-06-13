import { Controller, Get, UseGuards } from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { JwtAuthGuard } from "../../auth/guards/jwt-auth.guard";
import { NeighborhoodsService } from "./neighborhoods.service";
import type { NeighborhoodDto } from "../dto/neighborhood.dto";

@ApiTags("neighborhoods")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("api/v1/neighborhoods")
export class NeighborhoodsController {
  constructor(private readonly neighborhoodsService: NeighborhoodsService) {}

  @Get()
  @ApiOperation({ summary: "List neighborhoods" })
  findAll(): Promise<NeighborhoodDto[]> {
    return this.neighborhoodsService.findAll();
  }
}
