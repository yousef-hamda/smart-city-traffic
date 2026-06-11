export default function Home() {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        gap: "0.75rem",
        textAlign: "center",
        padding: "2rem",
      }}
    >
      <h1 style={{ fontSize: "2rem", margin: 0 }}>Developer Portal</h1>
      <p style={{ color: "#94a3b8", maxWidth: "32rem" }}>
        API catalog, key management, code samples, and an interactive explorer for the Smart City
        Traffic platform land here in Phase 16.
      </p>
    </main>
  );
}
