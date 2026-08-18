"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("cf-theme", next ? "dark" : "light");
    } catch {
      /* ignore */
    }
  }

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="btn btn-ghost !px-3"
      title={dark ? "Switch to light" : "Switch to dark"}
    >
      {mounted && dark ? <Sun size={16} /> : <Moon size={16} />}
      <span className="text-xs">{mounted ? (dark ? "Light" : "Dark") : "Theme"}</span>
    </button>
  );
}
