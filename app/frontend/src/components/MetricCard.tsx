export function MetricCard({ label, value, help }: { label: string; value: string | number; help?: string }) {
  return (
    <div className="figure">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {help && <span className="label">{help}</span>}
    </div>
  );
}
