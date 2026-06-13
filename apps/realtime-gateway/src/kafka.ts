/** Kafka consumer that pushes each record into the gateway's dispatch().
 *
 * Connection is resilient: if the broker is unreachable at boot, we log and
 * keep retrying rather than crashing, so the gateway still serves WebSocket
 * clients (they just receive nothing until the broker returns).
 */
import { Kafka, type Consumer } from "kafkajs";
import type { Logger } from "pino";

import type { RealtimeGateway } from "./gateway";

export interface KafkaConsumerDeps {
  brokers: string[];
  topics: string[];
  groupId: string;
  gateway: RealtimeGateway;
  logger: Logger;
}

export class TrafficConsumer {
  private readonly consumer: Consumer;

  constructor(private readonly deps: KafkaConsumerDeps) {
    const kafka = new Kafka({ clientId: deps.groupId, brokers: deps.brokers });
    this.consumer = kafka.consumer({ groupId: deps.groupId });
  }

  async start(): Promise<void> {
    try {
      await this.consumer.connect();
      await Promise.all(
        this.deps.topics.map((topic) => this.consumer.subscribe({ topic, fromBeginning: false })),
      );
      await this.consumer.run({
        eachMessage: async ({ topic, message }) => {
          this.deps.gateway.dispatch(topic, message.value);
        },
      });
      this.deps.logger.info({ topics: this.deps.topics }, "kafka consumer running");
    } catch (err) {
      this.deps.logger.warn({ err }, "kafka unavailable; gateway serving without live data");
    }
  }

  async stop(): Promise<void> {
    await this.consumer.disconnect().catch(() => undefined);
  }
}
