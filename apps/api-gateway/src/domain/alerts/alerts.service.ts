import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import type { PaginationQueryDto } from "../dto/pagination.dto";
import { PaginatedResponseDto } from "../dto/pagination.dto";
import type { AlertDto } from "../dto/alert.dto";

@Injectable()
export class AlertsService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(pagination: PaginationQueryDto): Promise<PaginatedResponseDto<AlertDto>> {
    const page = pagination.page ?? 1;
    const limit = pagination.limit ?? 20;
    const skip = (page - 1) * limit;

    const [rawItems, total] = await Promise.all([
      this.prisma.alert.findMany({
        skip,
        take: limit,
        select: {
          id: true,
          segmentId: true,
          alertType: true,
          severity: true,
          message: true,
          payload: true,
          createdAt: true,
          acknowledgedAt: true,
        },
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.alert.count(),
    ]);

    const items: AlertDto[] = rawItems.map((item) => ({
      ...item,
      payload: item.payload as Record<string, unknown> | null,
    }));

    return PaginatedResponseDto.of<AlertDto>(items, total, page, limit);
  }
}
