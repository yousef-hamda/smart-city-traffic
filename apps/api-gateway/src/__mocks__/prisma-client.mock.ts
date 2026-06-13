// Mock for @prisma/client used in unit tests
// Re-exports a minimal PrismaClient type stub so imports compile without a real DB.

export const PrismaClient = jest.fn().mockImplementation(() => ({
  $connect: jest.fn(),
  $disconnect: jest.fn(),
  user: { findUnique: jest.fn(), create: jest.fn(), findMany: jest.fn() },
  refreshToken: {
    create: jest.fn(),
    findFirst: jest.fn(),
    update: jest.fn(),
    updateMany: jest.fn(),
  },
  apiKey: {
    create: jest.fn(),
    findMany: jest.fn(),
    findUnique: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
  roadSegment: { findMany: jest.fn(), findUnique: jest.fn() },
  incident: { findMany: jest.fn() },
  alert: { findMany: jest.fn() },
  neighborhood: { findMany: jest.fn() },
  prediction: { findFirst: jest.fn(), findMany: jest.fn() },
}));

export type Prisma = Record<string, unknown>;
