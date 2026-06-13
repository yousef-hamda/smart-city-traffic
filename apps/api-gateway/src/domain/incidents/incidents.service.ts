import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import type { PaginationQueryDto } from "../dto/pagination.dto";
import { PaginatedResponseDto } from "../dto/pagination.dto";
import type { IncidentDto } from "../dto/incident.dto";

@Injectable()
export class IncidentsService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(pagination: PaginationQueryDto): Promise<PaginatedResponseDto<IncidentDto>> {
    const page = pagination.page ?? 1;
    const limit = pagination.limit ?? 20;
    const skip = (page - 1) * limit;

    const [items, total] = await Promise.all([
      this.prisma.incident.findMany({
        skip,
        take: limit,
        select: {
          id: true,
          segmentId: true,
          incidentType: true,
          severity: true,
          source: true,
          reporterUserId: true,
          detectedAt: true,
          resolvedAt: true,
          description: true,
        },
        orderBy: { detectedAt: "desc" },
      }),
      this.prisma.incident.count(),
    ]);

    return PaginatedResponseDto.of<IncidentDto>(items, total, page, limit);
  }
}
