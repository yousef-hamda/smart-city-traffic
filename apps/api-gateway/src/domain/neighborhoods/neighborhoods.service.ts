import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import type { NeighborhoodDto } from "../dto/neighborhood.dto";

@Injectable()
export class NeighborhoodsService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(): Promise<NeighborhoodDto[]> {
    return this.prisma.neighborhood.findMany({
      select: {
        id: true,
        nameEn: true,
        nameHe: true,
        nameAr: true,
      },
      orderBy: { nameEn: "asc" },
    });
  }
}
