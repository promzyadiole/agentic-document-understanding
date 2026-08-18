"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Boxes,
  ArrowRight,
  FileScan,
  Bot,
  Eye,
  TrendingUp,
  Mail,
  Sparkles,
} from "lucide-react";
import ThemeToggle from "@/components/theme-toggle";
import { Card } from "@/components/ui";
import { motion, Reveal, StaggerGroup, StaggerItem, staggerContainer, staggerItem } from "@/components/motion";
import { getAgencyProfile, submitContact } from "@/lib/api";

const FALLBACK = {
  firm_name: "Proziem Digital Global",
  tagline: "AI, automation, and digital growth for ambitious teams.",
  contact_email: "promzy007adiole@yahoo.com",
  capability_statement:
    "Proziem Digital Global builds AI systems and digital products that automate knowledge-intensive workflows: agentic document understanding, LLM and RAG applications, computer vision, robotics, and digital growth. We turn fragmented data into grounded, auditable decisions.",
  stats: [
    { value: "$13M+", label: "Revenue generated for clients" },
    { value: "75+", label: "Projects delivered" },
    { value: "6 yrs", label: "In business" },
  ],
  services: [
    { title: "Agentic Document Intelligence", description: "OCR, LLM extraction, validation, and grounded RAG over invoices, contracts, and reports." },
    { title: "LLM & RAG Applications", description: "Custom copilots and retrieval systems that answer from your own documents with citations." },
    { title: "Computer Vision & Robotics", description: "Perception, segmentation, and language-grounded autonomy for real-world systems." },
    { title: "Digital Growth & Automation", description: "Lead generation, outreach, and marketing systems that compound into measurable revenue." },
  ],
  portfolio: [
    { title: "Jama's Concept Digital Growth", subtitle: "45% increase in online tech-course enrollments in 60 days.", tag: "Growth" },
    { title: "MediNotes Pro", subtitle: "AI assistant that turns consultation notes into summaries, actions, and emails.", tag: "Product" },
    { title: "Language-Vision Robot Navigation", subtitle: "A ROS 2 robot that navigates using natural language and vision-language models.", tag: "R&D" },
    { title: "ConstructionFlow AI", subtitle: "Agentic document understanding for construction & procurement.", tag: "Platform" },
  ],
  team: [
    { name: "Promise Adiole", role: "CEO", bio: "Leads Proziem Digital Global from strategy through delivery." },
    { name: "Favour Emeziem", role: "Data & AI", bio: "Leads data and AI initiatives at Proziem Digital Global." },
  ],
};

const SERVICE_ICONS = [FileScan, Bot, Eye, TrendingUp];

export default function LandingPage() {
  const [p, setP] = useState<any>(FALLBACK);
  const [form, setForm] = useState({ name: "", email: "", company: "", message: "" });
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [contactError, setContactError] = useState("");

  useEffect(() => {
    getAgencyProfile()
      .then((data) => data?.firm_name && setP(data))
      .catch(() => {});
  }, []);

  async function handleContact(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.message.trim()) return;
    setSending(true);
    setContactError("");
    try {
      await submitContact(form);
      setSent(true);
      setForm({ name: "", email: "", company: "", message: "" });
    } catch (err: any) {
      setContactError(err.message || "Could not send message");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="app-canvas min-h-screen">
      {/* Nav */}
      <motion.header
        initial={{ y: -24, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="sticky top-0 z-30 border-b border-border bg-surface/70 backdrop-blur"
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <motion.span
              whileHover={{ rotate: 12, scale: 1.08 }}
              transition={{ type: "spring", stiffness: 400, damping: 12 }}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-strong text-white shadow-lg"
            >
              <Boxes size={18} />
            </motion.span>
            <span className="text-sm font-bold text-text">{p.firm_name}</span>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link href="/dashboard" className="btn btn-primary">
              Enter Platform <ArrowRight size={15} />
            </Link>
          </div>
        </div>
      </motion.header>

      {/* Hero */}
      <section className="relative mx-auto max-w-6xl overflow-hidden px-4 pb-16 pt-14 sm:px-6 sm:pt-20">
        {/* Animated glow */}
        <motion.div
          aria-hidden
          className="pointer-events-none absolute left-1/2 top-0 -z-0 h-72 w-72 -translate-x-1/2 rounded-full bg-brand/25 blur-[100px]"
          animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="relative mx-auto max-w-3xl text-center"
        >
          <motion.span variants={staggerItem} className="chip bg-brand-soft text-brand-strong">
            <Sparkles size={12} /> AI · Automation · Digital Growth
          </motion.span>
          <motion.h1
            variants={staggerItem}
            className="mt-5 text-4xl font-bold leading-tight tracking-tight text-text sm:text-6xl"
          >
            {p.tagline}
          </motion.h1>
          <motion.p
            variants={staggerItem}
            className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-text-muted sm:text-lg"
          >
            {p.capability_statement}
          </motion.p>
          <motion.div variants={staggerItem} className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link href="/dashboard" className="btn btn-primary !px-6 !py-3">
              Explore the platform <ArrowRight size={16} />
            </Link>
            <a href={`mailto:${p.contact_email}`} className="btn btn-ghost !px-6 !py-3">
              <Mail size={16} /> Let&apos;s talk
            </a>
          </motion.div>
        </motion.div>

        {/* Stats */}
        <StaggerGroup className="relative mx-auto mt-14 grid max-w-3xl grid-cols-3 gap-4">
          {p.stats.map((s: any, i: number) => (
            <StaggerItem key={i} className="card p-5 text-center">
              <p className="bg-gradient-to-br from-brand to-brand-strong bg-clip-text text-2xl font-bold text-transparent sm:text-3xl">
                {s.value}
              </p>
              <p className="mt-1 text-xs text-text-muted">{s.label}</p>
            </StaggerItem>
          ))}
        </StaggerGroup>
      </section>

      {/* Services */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Reveal className="mb-8 text-center">
          <p className="label-caps text-brand">What we do</p>
          <h2 className="mt-2 text-2xl font-bold text-text sm:text-3xl">Services</h2>
        </Reveal>
        <StaggerGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {p.services.map((s: any, i: number) => {
            const Icon = SERVICE_ICONS[i % SERVICE_ICONS.length];
            return (
              <StaggerItem key={i} className="card h-full p-6">
                <motion.span
                  whileHover={{ rotate: -8, scale: 1.1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 12 }}
                  className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-brand"
                >
                  <Icon size={20} />
                </motion.span>
                <h3 className="mt-4 text-sm font-semibold text-text">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-text-muted">{s.description}</p>
              </StaggerItem>
            );
          })}
        </StaggerGroup>
      </section>

      {/* Portfolio */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Reveal className="mb-8 text-center">
          <p className="label-caps text-brand">Selected work</p>
          <h2 className="mt-2 text-2xl font-bold text-text sm:text-3xl">Portfolio</h2>
        </Reveal>
        <StaggerGroup className="grid gap-4 sm:grid-cols-2">
          {p.portfolio.map((w: any, i: number) => (
            <StaggerItem key={i} className="card flex items-start justify-between gap-4 p-6">
              <div>
                <h3 className="text-sm font-semibold text-text">{w.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-text-muted">{w.subtitle}</p>
              </div>
              <span className="chip shrink-0 bg-accent-soft text-accent">{w.tag}</span>
            </StaggerItem>
          ))}
        </StaggerGroup>
      </section>

      {/* Team + CTA */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Reveal>
          <div className="card overflow-hidden">
            <div className="grid gap-8 p-8 sm:grid-cols-2 sm:p-10">
              <div>
                <p className="label-caps text-brand">The team</p>
                <div className="mt-4 space-y-4">
                  {p.team.map((t: any, i: number) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-brand text-sm font-bold text-white">
                        {t.name.split(" ").map((n: string) => n[0]).join("")}
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-text">{t.name} · <span className="text-text-muted">{t.role}</span></p>
                        <p className="text-xs text-text-muted">{t.bio}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col justify-center">
                <h3 className="text-xl font-bold text-text">Ready to build something great?</h3>
                <p className="mt-2 text-sm text-text-muted">
                  Run the document-intelligence platform, discover leads, and generate aligned proposals — end to end.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  <Link href="/dashboard" className="btn btn-primary">
                    Enter Platform <ArrowRight size={15} />
                  </Link>
                  <a href={`mailto:${p.contact_email}`} className="btn btn-ghost">
                    <Mail size={15} /> {p.contact_email}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Contact */}
      <section id="contact" className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Reveal>
          <Card className="grid gap-8 p-8 sm:grid-cols-2 sm:p-10">
            <div>
              <p className="label-caps text-brand">Contact us</p>
              <h2 className="mt-2 text-2xl font-bold text-text sm:text-3xl">Tell us about your project</h2>
              <p className="mt-3 text-sm leading-relaxed text-text-muted">
                Every message is classified and routed to our team automatically — and processed
                through our own document-understanding workflow. We&apos;ll get back to you fast.
              </p>
              <a href={`mailto:${p.contact_email}`} className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-brand hover:text-brand-strong">
                <Mail size={15} /> {p.contact_email}
              </a>
            </div>

            {sent ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center rounded-xl border border-ok-soft bg-ok-soft p-8 text-center text-ok"
              >
                <Sparkles size={28} />
                <p className="mt-3 text-sm font-semibold">Message received!</p>
                <p className="mt-1 text-sm">Thanks — our team has it and will reach out shortly.</p>
                <button onClick={() => setSent(false)} className="btn btn-ghost mt-4">
                  Send another
                </button>
              </motion.div>
            ) : (
              <form onSubmit={handleContact} className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input" placeholder="Your name" />
                  <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input" placeholder="Email" />
                </div>
                <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} className="input" placeholder="Company (optional)" />
                <textarea required value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} className="input min-h-[120px] resize-y" placeholder="How can we help?" />
                {contactError ? (
                  <p className="rounded-lg border border-danger-soft bg-danger-soft px-3 py-2 text-xs text-danger">{contactError}</p>
                ) : null}
                <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }} type="submit" disabled={sending} className="btn btn-primary w-full">
                  <Mail size={15} /> {sending ? "Sending…" : "Send message"}
                </motion.button>
              </form>
            )}
          </Card>
        </Reveal>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-text-faint sm:px-6">
          © {new Date().getFullYear()} {p.firm_name}. Built with LangGraph · FastAPI · OpenAI · Next.js.
        </div>
      </footer>
    </div>
  );
}
