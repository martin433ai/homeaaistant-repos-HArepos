import React from "react";
import Icon from "./components/Icon";

const App = () => {
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.logoContainer}>
          <Icon size={32} color="#03a9f4" flag={true} />
          <h1 style={styles.title}>Home Assistant</h1>
        </div>
        <nav style={styles.nav}>
          <button style={styles.navButton}>Dashboard</button>
          <button style={styles.navButton}>Devices</button>
          <button style={styles.navButton}>Automations</button>
          <button style={styles.navButton}>Settings</button>
        </nav>
      </header>
      <main style={styles.main}>
        <div style={styles.dashboard}>
          <h2 style={styles.sectionTitle}>Welcome to your Home Assistant</h2>
          <p style={styles.description}>
            Control your smart home devices and view their status from this dashboard.
          </p>
          <div style={styles.cardContainer}>
            {[1, 2, 3, 4].map((item) => (
              <div key={item} style={styles.card}>
                <h3 style={styles.cardTitle}>Device {item}</h3>
                <p style={styles.cardContent}>Status: Online</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

// Styles
const styles: {
  container: React.CSSProperties;
  header: React.CSSProperties;
  logoContainer: React.CSSProperties;
  title: React.CSSProperties;
  nav: React.CSSProperties;
  navButton: React.CSSProperties;
  main: React.CSSProperties;
  dashboard: React.CSSProperties;
  sectionTitle: React.CSSProperties;
  description: React.CSSProperties;
  cardContainer: React.CSSProperties;
  card: React.CSSProperties;
  cardTitle: React.CSSProperties;
  cardContent: React.CSSProperties;
} = {
  container: {
    fontFamily: "'Roboto', 'Segoe UI', Arial, sans-serif",
    maxWidth: "100vw",
    minHeight: "100vh",
    backgroundColor: "#f5f7fa",
    margin: 0,
    padding: 0
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.5rem 1.5rem",
    backgroundColor: "#ffffff",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
    position: "sticky",
    top: 0,
    zIndex: 100
  },
  logoContainer: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem"
  },
  title: {
    fontSize: "1.25rem",
    fontWeight: 600,
    color: "#2c3e50",
    margin: 0
  },
  nav: {
    display: "flex",
    gap: "1rem"
  },
  navButton: {
    border: "none",
    background: "none",
    padding: "0.5rem 0.75rem",
    fontSize: "0.9rem",
    color: "#5c6a7a",
    cursor: "pointer",
    borderRadius: "4px",
    transition: "background-color 0.2s, color 0.2s",
    fontWeight: 500
  },
  main: {
    padding: "2rem",
    maxWidth: "1200px",
    margin: "0 auto"
  },
  dashboard: {
    width: "100%"
  },
  sectionTitle: {
    fontSize: "1.5rem",
    color: "#2c3e50",
    marginBottom: "1rem"
  },
  description: {
    color: "#5c6a7a",
    marginBottom: "2rem"
  },
  cardContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
    gap: "1.5rem"
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: "8px",
    padding: "1.5rem",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.05)",
    transition: "transform 0.2s, box-shadow 0.2s",
    cursor: "pointer"
  },
  cardTitle: {
    fontSize: "1.1rem",
    color: "#2c3e50",
    marginTop: 0,
    marginBottom: "0.75rem"
  },
  cardContent: {
    color: "#5c6a7a",
    margin: 0
  }
};

export default App;
