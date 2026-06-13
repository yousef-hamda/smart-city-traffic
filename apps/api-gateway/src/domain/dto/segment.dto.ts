import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class SegmentDto {
  @ApiProperty()
  id!: string;

  @ApiPropertyOptional()
  roadId?: string | null;

  @ApiPropertyOptional()
  seq?: number | null;

  @ApiProperty()
  nameEn!: string;

  @ApiPropertyOptional()
  nameHe?: string | null;

  @ApiPropertyOptional()
  nameAr?: string | null;

  @ApiPropertyOptional()
  segmentType?: string | null;

  @ApiPropertyOptional()
  speedLimitKmh?: number | null;

  @ApiPropertyOptional()
  lanes?: number | null;

  @ApiPropertyOptional()
  neighborhoodId?: string | null;
}
