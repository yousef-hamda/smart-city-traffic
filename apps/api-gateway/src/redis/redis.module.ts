import { Global, Module } from "@nestjs/common";
import { RedisService } from "./redis.service";
import { REDIS_CLIENT } from "./redis.interface";

@Global()
@Module({
  providers: [
    {
      provide: REDIS_CLIENT,
      useClass: RedisService,
    },
    RedisService,
  ],
  exports: [REDIS_CLIENT, RedisService],
})
export class RedisModule {}
