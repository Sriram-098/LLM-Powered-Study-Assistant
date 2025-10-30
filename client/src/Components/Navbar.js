import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: 12, borderBottom: "1px solid #eee" }}>
      <Link to="/">Home</Link> {" | "}
      <Link to="/upload">Upload</Link> {" | "}
      <Link to="/history">History</Link> {" | "}
      <Link to="/login">Login</Link> {" | "}
      <Link to="/register">Register</Link>
    </nav>
  );
}
