/**
 * OpenTelemetry bootstrap for the API gateway.
 *
 * This module MUST be imported before any other application code (see
 * `src/main.ts`) so that auto-instrumentations can patch modules at
 * require-time.
 *
 * The SDK is only started when OTEL_EXPORTER_OTLP_ENDPOINT is set, so local
 * development without a collector incurs zero overhead.
 */
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { NodeSDK } from '@opentelemetry/sdk-node';

const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;

export let otelSdk: NodeSDK | undefined;

if (otlpEndpoint) {
  otelSdk = new NodeSDK({
    serviceName: process.env.OTEL_SERVICE_NAME ?? 'api-gateway',
    traceExporter: new OTLPTraceExporter({ url: otlpEndpoint }),
    instrumentations: [getNodeAutoInstrumentations()],
  });

  otelSdk.start();

  const shutdown = (): void => {
    otelSdk
      ?.shutdown()
      .catch((err: unknown) =>
        // eslint-disable-next-line no-console
        console.error('Error shutting down OpenTelemetry SDK', err),
      )
      .finally(() => process.exit(0));
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}
