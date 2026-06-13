module.exports = {
  root: true,
  extends: ["expo"],
  overrides: [
    {
      files: ["**/__tests__/**/*", "**/__mocks__/**/*", "jest.setup.js"],
      env: {
        jest: true,
      },
    },
  ],
};
