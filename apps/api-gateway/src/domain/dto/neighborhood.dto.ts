import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class NeighborhoodDto {
  @ApiProperty()
  id!: string;

  @ApiProperty()
  nameEn!: string;

  @ApiPropertyOptional()
  nameHe?: string | null;

  @ApiPropertyOptional()
  nameAr?: string | null;
}
