import { Controller, Get } from '@nestjs/common';

/** Keep in sync with package.json "version". */
const SERVICE_VERSION = '0.1.0';

export interface HealthResponse {
  status: 'ok';
  service: 'api-gateway';
  version: string;
}

@Controller('health')
export class HealthController {
  @Get()
  getHealth(): HealthResponse {
    return {
      status: 'ok',
      service: 'api-gateway',
      version: SERVICE_VERSION,
    };
  }
}
