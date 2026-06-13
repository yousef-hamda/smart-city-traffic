// Jest setup — global mocks for native modules that aren't available in Jest

// AsyncStorage mock
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock"),
);

// expo-secure-store mock
jest.mock("expo-secure-store", () => require("./__mocks__/expo-secure-store.js"));

// expo-notifications mock
jest.mock("expo-notifications", () => require("./__mocks__/expo-notifications.js"));

// expo-image-picker mock
jest.mock("expo-image-picker", () => require("./__mocks__/expo-image-picker.js"));

// react-native-maps mock
jest.mock("react-native-maps", () => require("./__mocks__/react-native-maps.js"));
