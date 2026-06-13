const React = require("react");

function MockMapView({ children, testID, ...props }) {
  return React.createElement("View", { testID: testID || "map-view", ...props }, children);
}

function MockPolyline({ testID, ...props }) {
  return React.createElement("View", { testID: testID || "polyline", ...props });
}

function MockMarker({ testID, ...props }) {
  return React.createElement("View", { testID: testID || "marker", ...props });
}

module.exports = MockMapView;
module.exports.default = MockMapView;
module.exports.Polyline = MockPolyline;
module.exports.Marker = MockMarker;
module.exports.PROVIDER_GOOGLE = "google";
