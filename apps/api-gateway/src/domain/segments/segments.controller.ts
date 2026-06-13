import { Controller, Get, NotFoundException, Param, Query, UseGuards } from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { JwtAuthGuard } from "../../auth/guards/jwt-auth.guard";
import { SegmentsService } from "./segments.service";
import { PaginationQueryDto, PaginatedResponseDto } from "../dto/pagination.dto";
import type { SegmentDto } from "../dto/segment.dto";

@ApiTags("segments")
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller("api/v1/segments")
export class SegmentsController {
  constructor(private readonly segmentsService: SegmentsService) {}

  @Get()
  @ApiOperation({ summary: "List road segments" })
  findAll(@Query() pagination: PaginationQueryDto): Promise<PaginatedResponseDto<SegmentDto>> {
    return this.segmentsService.findAll(pagination);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get a road segment by ID" })
  async findOne(@Param("id") id: string): Promise<SegmentDto> {
    const segment = await this.segmentsService.findOne(id);
    if (!segment) {
      throw new NotFoundException(`Segment ${id} not found`);
    }
    return segment;
  }
}
