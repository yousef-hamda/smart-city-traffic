import { Module } from "@nestjs/common";
import { SegmentsService } from "./segments/segments.service";
import { SegmentsController } from "./segments/segments.controller";
import { IncidentsService } from "./incidents/incidents.service";
import { IncidentsController } from "./incidents/incidents.controller";
import { AlertsService } from "./alerts/alerts.service";
import { AlertsController } from "./alerts/alerts.controller";
import { NeighborhoodsService } from "./neighborhoods/neighborhoods.service";
import { NeighborhoodsController } from "./neighborhoods/neighborhoods.controller";

@Module({
  controllers: [SegmentsController, IncidentsController, AlertsController, NeighborhoodsController],
  providers: [SegmentsService, IncidentsService, AlertsService, NeighborhoodsService],
})
export class DomainModule {}
