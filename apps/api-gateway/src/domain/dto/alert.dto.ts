import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class AlertDto {
  @ApiProperty()
  id!: string;

  @ApiPropertyOptional()
  segmentId?: string | null;

  @ApiPropertyOptional()
  alertType?: string | null;

  @ApiPropertyOptional()
  severity?: string | null;

  @ApiPropertyOptional()
  message?: string | null;

  @ApiPropertyOptional()
  payload?: Record<string, unknown> | null;

  @ApiPropertyOptional()
  createdAt?: Date | null;

  @ApiPropertyOptional()
  acknowledgedAt?: Date | null;
}
