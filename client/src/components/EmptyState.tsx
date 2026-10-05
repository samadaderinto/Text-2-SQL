import { FiInbox } from "react-icons/fi";

type EmptyStateProps = {
  title: string;
  description: string;
};

export const EmptyState = ({ title, description }: EmptyStateProps) => (
  <section className="App_Empty_State">
    <b className="App_Empty_Icon" aria-hidden="true"><FiInbox /></b>
    <strong>{title}</strong>
    <small>{description}</small>
  </section>
);
