export default function Topbar({
  title,
  subtitle,
}: {
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">{title}</h1>
        {subtitle ? (
          <p className="mt-2 max-w-3xl text-sm text-gray-600">{subtitle}</p>
        ) : null}
      </div>
    </div>
  );
}