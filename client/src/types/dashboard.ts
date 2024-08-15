import { ReactElement } from "react";

export interface DashboardCardProps {
    icon: ReactElement,
    title: string,
    value: number,
    percent: number,
    increment: number
  }