import express, { Express, Request, Response } from 'express';

/** Keep in sync with package.json "version". */
export const SERVICE_VERSION = '0.1.0';
export const SERVICE_NAME = 'realtime-gateway';

export interface HealthResponse {
  status: 'ok';
  service: string;
  version: string;
}

/**
 * The bare Express app, exported separately from the HTTP/Socket.IO server so
 * supertest can exercise routes without binding a port.
 */
export function createApp(): Express {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json());

  app.get('/health', (_req: Request, res: Response<HealthResponse>) => {
    res.status(200).json({
      status: 'ok',
      service: SERVICE_NAME,
      version: SERVICE_VERSION,
    });
  });

  return app;
}
