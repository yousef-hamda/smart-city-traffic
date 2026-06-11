import { Incident, IncidentSchema, SensorReading, SensorReadingSchema } from '../index';

describe('SensorReadingSchema', () => {
  const reading: SensorReading = {
    sensorId: 'sensor-0042',
    ts: '2026-06-11T08:30:00.000Z',
    lat: 32.0853,
    lon: 34.7818,
    vehicleCount: 17,
    avgSpeedKmh: 43.5,
    occupancyPct: 62.4,
  };

  it('round-trips a valid reading through parse -> serialize -> parse', () => {
    const parsed = SensorReadingSchema.parse(reading);
    expect(parsed).toEqual(reading);

    const reparsed = SensorReadingSchema.parse(JSON.parse(JSON.stringify(parsed)));
    expect(reparsed).toEqual(reading);
  });

  it('rejects out-of-range and malformed values', () => {
    expect(SensorReadingSchema.safeParse({ ...reading, occupancyPct: 120 }).success).toBe(false);
    expect(SensorReadingSchema.safeParse({ ...reading, vehicleCount: -1 }).success).toBe(false);
    expect(SensorReadingSchema.safeParse({ ...reading, ts: 'not-a-date' }).success).toBe(false);
  });
});

describe('IncidentSchema', () => {
  const incident: Incident = {
    incidentId: 'inc-001',
    segmentId: 'seg-101',
    type: 'accident',
    severity: 'high',
    status: 'open',
    startedAt: '2026-06-11T08:00:00.000Z',
    lat: 32.0809,
    lon: 34.7806,
    description: 'Two-vehicle collision blocking the right lane',
  };

  it('round-trips a valid incident through parse -> serialize -> parse', () => {
    const parsed = IncidentSchema.parse(incident);
    expect(parsed).toEqual(incident);

    const reparsed = IncidentSchema.parse(JSON.parse(JSON.stringify(parsed)));
    expect(reparsed).toEqual(incident);
  });

  it('rejects unknown enum values', () => {
    expect(IncidentSchema.safeParse({ ...incident, type: 'ufo_landing' }).success).toBe(false);
    expect(IncidentSchema.safeParse({ ...incident, severity: 'extreme' }).success).toBe(false);
  });
});
