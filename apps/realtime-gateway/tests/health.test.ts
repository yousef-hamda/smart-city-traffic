import request from 'supertest';

import { createApp } from '../src/app';

describe('GET /health', () => {
  it('returns service status without binding a port', async () => {
    const app = createApp();

    const response = await request(app).get('/health').expect(200);

    expect(response.body).toEqual({
      status: 'ok',
      service: 'realtime-gateway',
      version: expect.stringMatching(/^\d+\.\d+\.\d+$/),
    });
  });
});
