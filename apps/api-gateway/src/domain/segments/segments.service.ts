import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import type { PaginationQueryDto } from "../dto/pagination.dto";
import { PaginatedResponseDto } from "../dto/pagination.dto";
import type { SegmentDto } from "../dto/segment.dto";

@Injectable()
export class SegmentsService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(pagination: PaginationQueryDto): Promise<PaginatedResponseDto<SegmentDto>> {
    const page = pagination.page ?? 1;
    const limit = pagination.limit ?? 20;
    const skip = (page - 1) * limit;

    const [items, total] = await Promise.all([
      this.prisma.roadSegment.findMany({
        skip,
        take: limit,
        select: {
          id: true,
          roadId: true,
          seq: true,
          nameEn: true,
          nameHe: true,
          nameAr: true,
          segmentType: true,
          speedLimitKmh: true,
          lanes: true,
          neighborhoodId: true,
        },
        orderBy: { nameEn: "asc" },
      }),
      this.prisma.roadSegment.count(),
    ]);

    return PaginatedResponseDto.of<SegmentDto>(items, total, page, limit);
  }

  async findOne(id: string): Promise<SegmentDto | null> {
    const segment = await this.prisma.roadSegment.findUnique({
      where: { id },
      select: {
        id: true,
        roadId: true,
        seq: true,
        nameEn: true,
        nameHe: true,
        nameAr: true,
        segmentType: true,
        speedLimitKmh: true,
        lanes: true,
        neighborhoodId: true,
      },
    });

    return segment;
  }
}
