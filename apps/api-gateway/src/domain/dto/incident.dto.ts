import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class IncidentDto {
  @ApiProperty()
  id!: string;

  @ApiPropertyOptional()
  segmentId?: string | null;

  @ApiPropertyOptional()
  incidentType?: string | null;

  @ApiPropertyOptional()
  severity?: string | null;

  @ApiPropertyOptional()
  source?: string | null;

  @ApiPropertyOptional()
  reporterUserId?: string | null;

  @ApiPropertyOptional()
  detectedAt?: Date | null;

  @ApiPropertyOptional()
  resolvedAt?: Date | null;

  @ApiPropertyOptional()
  description?: string | null;
}
