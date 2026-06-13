import { ApiProperty } from "@nestjs/swagger";

export class AuthResponseDto {
  @ApiProperty()
  accessToken!: string;

  @ApiProperty({ default: "Bearer" })
  tokenType!: "Bearer";
}
