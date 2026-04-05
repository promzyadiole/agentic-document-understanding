export default function AgentTracePanel({ trace }: { trace: any }) {
  const history = trace?.history || [];
  const steps = trace?.steps_taken || [];

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900">Latest Agent Trace</h3>

      <div className="mt-4 space-y-3 text-sm text-gray-700">
        <p>
          <span className="font-medium">Final action:</span>{" "}
          {trace?.agent_action || "-"}
        </p>
        <p>
          <span className="font-medium">Loop count:</span>{" "}
          {trace?.loop_count ?? "-"}
        </p>
        <p>
          <span className="font-medium">Final reasoning:</span>{" "}
          {trace?.agent_reasoning || "-"}
        </p>
      </div>

      <div className="mt-5">
        <p className="text-sm font-medium text-gray-900">Step history</p>
        {steps.length === 0 ? (
          <p className="mt-2 text-sm text-gray-600">No steps recorded.</p>
        ) : (
          <div className="mt-3 flex flex-wrap gap-2">
            {steps.map((step: string, idx: number) => (
              <span
                key={`${step}-${idx}`}
                className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700"
              >
                {idx + 1}. {step}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-6">
        <p className="text-sm font-medium text-gray-900">Reasoning timeline</p>
        {history.length === 0 ? (
          <p className="mt-2 text-sm text-gray-600">No reasoning history available.</p>
        ) : (
          <div className="mt-3 space-y-3">
            {history.map((item: any, idx: number) => (
              <div key={idx} className="rounded-2xl bg-gray-50 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-black px-3 py-1 text-xs text-white">
                    Loop {item.loop_count ?? idx + 1}
                  </span>
                  <span className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-800">
                    {item.action || "unknown"}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-gray-700">
                  {item.reasoning || "-"}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}