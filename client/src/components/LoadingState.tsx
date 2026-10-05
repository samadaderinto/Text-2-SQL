type LoadingStateProps = {
  label?: string;
  compact?: boolean;
};

export const LoadingState = ({ label = "Loading your data", compact = false }: LoadingStateProps) => (
  <section className={`App_Loading_State${compact ? " compact" : ""}`} role="status" aria-live="polite">
    <b className="App_Loading_Mark" aria-hidden="true">
      <i />
      <i />
      <i />
    </b>
    <small>{label}</small>
  </section>
);
