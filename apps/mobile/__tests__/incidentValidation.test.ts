/**
 * Incident form validation logic tests.
 * Tests the validation rules extracted from the report screen.
 */

interface IncidentFormValues {
  latitude: string;
  longitude: string;
  type: "accident" | "pothole" | "blockage" | null;
  description: string;
}

interface ValidationErrors {
  location?: string;
  type?: string;
}

function validateIncidentForm(form: IncidentFormValues): ValidationErrors {
  const errors: ValidationErrors = {};

  const lat = parseFloat(form.latitude);
  const lng = parseFloat(form.longitude);
  if (!form.latitude.trim() || !form.longitude.trim() || isNaN(lat) || isNaN(lng)) {
    errors.location = "Location is required";
  }

  if (!form.type) {
    errors.type = "Incident type is required";
  }

  return errors;
}

describe("validateIncidentForm", () => {
  const validForm: IncidentFormValues = {
    latitude: "31.7683",
    longitude: "35.2137",
    type: "accident",
    description: "Rear-end collision at the intersection",
  };

  it("passes with all required fields filled", () => {
    const errors = validateIncidentForm(validForm);
    expect(Object.keys(errors)).toHaveLength(0);
  });

  it("requires a location (latitude)", () => {
    const errors = validateIncidentForm({ ...validForm, latitude: "" });
    expect(errors.location).toBeDefined();
    expect(errors.type).toBeUndefined();
  });

  it("requires a location (longitude)", () => {
    const errors = validateIncidentForm({ ...validForm, longitude: "" });
    expect(errors.location).toBeDefined();
  });

  it("rejects non-numeric latitude", () => {
    const errors = validateIncidentForm({ ...validForm, latitude: "abc" });
    expect(errors.location).toBeDefined();
  });

  it("rejects non-numeric longitude", () => {
    const errors = validateIncidentForm({ ...validForm, longitude: "xyz" });
    expect(errors.location).toBeDefined();
  });

  it("requires incident type selection", () => {
    const errors = validateIncidentForm({ ...validForm, type: null });
    expect(errors.type).toBeDefined();
    expect(errors.location).toBeUndefined();
  });

  it("returns both errors when both location and type are missing", () => {
    const errors = validateIncidentForm({ ...validForm, latitude: "", type: null });
    expect(errors.location).toBeDefined();
    expect(errors.type).toBeDefined();
  });

  it("accepts pothole type", () => {
    const errors = validateIncidentForm({ ...validForm, type: "pothole" });
    expect(Object.keys(errors)).toHaveLength(0);
  });

  it("accepts blockage type", () => {
    const errors = validateIncidentForm({ ...validForm, type: "blockage" });
    expect(Object.keys(errors)).toHaveLength(0);
  });

  it("allows empty description (optional field)", () => {
    const errors = validateIncidentForm({ ...validForm, description: "" });
    expect(Object.keys(errors)).toHaveLength(0);
  });
});
