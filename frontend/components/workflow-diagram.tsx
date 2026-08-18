"use client";

import { useState } from "react";

/**
 * Dependency-free, interactive rendering of the LangGraph document workflow.
 * Nodes visited by the most recent run are highlighted, and hovering a node
 * shows what it does. This is a live view of the real graph topology
 * (agent_reason is the hub that routes to every tool and loops back).
 */

type NodeDef = {
  id: string;
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  desc: string;
  hub?: boolean;
  terminal?: boolean;
};

const NODES: NodeDef[] = [
  { id: "__start__", label: "START", x: 20, y: 214, w: 74, h: 40, desc: "Workflow entry point." , terminal: true},
  { id: "document_intake", label: "document_intake", x: 116, y: 210, w: 150, h: 48, desc: "OCR or native parsing of the uploaded file into text." },
  { id: "agent_reason", label: "agent_reason", x: 300, y: 186, w: 156, h: 96, desc: "The controller. Inspects state and decides the next action — the loop's brain.", hub: true },
  { id: "clean_text", label: "clean_text", x: 560, y: 14, w: 190, h: 44, desc: "Normalize and de-noise OCR text." },
  { id: "classify_document", label: "classify_document", x: 560, y: 74, w: 190, h: 44, desc: "LLM classifies the document type." },
  { id: "index_document", label: "index_document", x: 560, y: 134, w: 190, h: 44, desc: "Embed chunks and upsert into Pinecone." },
  { id: "extract_fields", label: "extract_fields", x: 560, y: 210, w: 190, h: 44, desc: "Schema-constrained LLM extraction with evidence spans." },
  { id: "validate_document", label: "validate_document", x: 560, y: 286, w: 190, h: 44, desc: "Validate fields; failures trigger self-correcting re-extraction." },
  { id: "log_kpis", label: "log_kpis", x: 560, y: 346, w: 190, h: 44, desc: "Compute and persist quality KPIs." },
  { id: "__end__", label: "END", x: 346, y: 410, w: 74, h: 40, desc: "Workflow finished.", terminal: true },
];

const TOOL_IDS = [
  "clean_text",
  "classify_document",
  "index_document",
  "extract_fields",
  "validate_document",
  "log_kpis",
];

function centerRight(n: NodeDef) {
  return { x: n.x + n.w, y: n.y + n.h / 2 };
}
function centerLeft(n: NodeDef) {
  return { x: n.x, y: n.y + n.h / 2 };
}

export default function WorkflowDiagram({ steps }: { steps?: string[] }) {
  const [hover, setHover] = useState<string | null>(null);
  const visited = new Set((steps || []).map((s) => s.replace(/_skipped$|_retry$/, "")));
  visited.add("__start__");
  if ((steps || []).length) visited.add("__end__");

  const byId = (id: string) => NODES.find((n) => n.id === id)!;
  const hub = byId("agent_reason");
  const hubRight = centerRight(hub);
  const hubBottom = { x: hub.x + hub.w / 2, y: hub.y + hub.h };

  const isVisited = (id: string) => visited.has(id);

  return (
    <div className="w-full">
      <div className="relative w-full overflow-x-auto">
        <svg viewBox="0 0 780 470" className="h-auto w-full min-w-[560px]" role="img" aria-label="LangGraph workflow diagram">
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="var(--border-strong)" />
            </marker>
            <marker id="arrow-brand" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="var(--brand)" />
            </marker>
          </defs>

          {/* START -> intake -> agent_reason */}
          <line x1={94} y1={234} x2={116} y2={234} stroke="var(--border-strong)" strokeWidth={1.5} markerEnd="url(#arrow)" />
          <line x1={266} y1={234} x2={300} y2={234} stroke="var(--border-strong)" strokeWidth={1.5} markerEnd="url(#arrow)" />

          {/* hub -> each tool (route) */}
          {TOOL_IDS.map((id) => {
            const n = byId(id);
            const to = centerLeft(n);
            const active = isVisited(id);
            const mx = (hubRight.x + to.x) / 2;
            return (
              <path
                key={`edge-${id}`}
                d={`M ${hubRight.x} ${hubRight.y} C ${mx} ${hubRight.y}, ${mx} ${to.y}, ${to.x} ${to.y}`}
                fill="none"
                stroke={active ? "var(--brand)" : "var(--border)"}
                strokeWidth={active ? 1.8 : 1.2}
                markerEnd={active ? "url(#arrow-brand)" : "url(#arrow)"}
                opacity={active ? 1 : 0.6}
              />
            );
          })}

          {/* representative return arrow (loop back) */}
          <path
            d={`M 750 400 C 500 452, 360 400, ${hubBottom.x + 30} ${hubBottom.y}`}
            fill="none"
            stroke="var(--border-strong)"
            strokeWidth={1.3}
            strokeDasharray="5 4"
            markerEnd="url(#arrow)"
          />
          <text x={470} y={444} fill="var(--text-faint)" fontSize={10} fontStyle="italic">
            returns to agent_reason after each step
          </text>

          {/* hub -> END */}
          <line
            x1={hub.x + hub.w / 2}
            y1={hub.y + hub.h}
            x2={383}
            y2={410}
            stroke={isVisited("__end__") ? "var(--brand)" : "var(--border-strong)"}
            strokeWidth={1.6}
            markerEnd={isVisited("__end__") ? "url(#arrow-brand)" : "url(#arrow)"}
          />
          <text x={392} y={356} fill="var(--text-faint)" fontSize={10} fontStyle="italic">
            finish
          </text>

          {/* Nodes */}
          {NODES.map((n) => {
            const active = isVisited(n.id);
            const isHover = hover === n.id;
            const fill = n.terminal
              ? "var(--surface-2)"
              : active
              ? "var(--brand-soft)"
              : "var(--surface)";
            const stroke = active ? "var(--brand)" : "var(--border-strong)";
            return (
              <g
                key={n.id}
                onMouseEnter={() => setHover(n.id)}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: "default" }}
              >
                <rect
                  x={n.x}
                  y={n.y}
                  width={n.w}
                  height={n.h}
                  rx={n.terminal ? 20 : 12}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={n.hub ? 2.2 : isHover ? 2 : 1.3}
                />
                <text
                  x={n.x + n.w / 2}
                  y={n.y + n.h / 2 + (n.hub ? -4 : 4)}
                  textAnchor="middle"
                  fontSize={n.hub ? 13 : 11}
                  fontWeight={n.hub || n.terminal ? 700 : 500}
                  fill={active || n.hub ? "var(--brand-strong)" : "var(--text)"}
                  fontFamily="var(--font-mono)"
                >
                  {n.label}
                </text>
                {n.hub ? (
                  <text x={n.x + n.w / 2} y={n.y + n.h / 2 + 16} textAnchor="middle" fontSize={9.5} fill="var(--text-muted)">
                    ⟲ decides next step
                  </text>
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>

      {hover ? (
        <div className="mt-3 rounded-xl border border-border bg-surface-2 px-4 py-2.5 text-sm">
          <span className="font-mono font-semibold text-brand">{byId(hover).label}</span>
          <span className="text-text-muted"> — {byId(hover).desc}</span>
        </div>
      ) : (
        <p className="mt-3 text-xs text-text-faint">
          Hover a node for details. Highlighted nodes were visited by the latest run.
        </p>
      )}
    </div>
  );
}
