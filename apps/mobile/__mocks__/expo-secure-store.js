const store = new Map();

module.exports = {
  setItemAsync: jest.fn((key, value) => {
    store.set(key, value);
    return Promise.resolve();
  }),
  getItemAsync: jest.fn((key) => {
    return Promise.resolve(store.get(key) ?? null);
  }),
  deleteItemAsync: jest.fn((key) => {
    store.delete(key);
    return Promise.resolve();
  }),
  AFTER_FIRST_UNLOCK: "afterFirstUnlock",
  AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY: "afterFirstUnlockThisDeviceOnly",
  ALWAYS: "always",
  WHEN_PASSCODE_SET_THIS_DEVICE_ONLY: "whenPasscodeSetThisDeviceOnly",
  ALWAYS_THIS_DEVICE_ONLY: "alwaysThisDeviceOnly",
  WHEN_UNLOCKED: "whenUnlocked",
  WHEN_UNLOCKED_THIS_DEVICE_ONLY: "whenUnlockedThisDeviceOnly",
};
