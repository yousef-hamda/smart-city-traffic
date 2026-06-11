// OpenTelemetry must be imported (and started) before anything else so that
// auto-instrumentations can hook module loading.
import './telemetry/otel';

import { NestFactory } from '@nestjs/core';

import { AppModule } from './app.module';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);

  // TODO(Phase 9): enable a global ValidationPipe once DTOs land, e.g.
  //   app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  // (requires class-validator + class-transformer, added with the first DTOs).

  app.enableShutdownHooks();

  const port = Number(process.env.PORT ?? 8080);
  await app.listen(port);
  // eslint-disable-next-line no-console
  console.log(`api-gateway listening on port ${port}`);
}

void bootstrap();
