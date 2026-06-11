import { render, screen } from "@testing-library/react-native";

import Home from "../app/index";

describe("Home screen", () => {
  it("renders the app title", () => {
    render(<Home />);
    expect(screen.getByText("Smart City Traffic")).toBeTruthy();
  });
});
