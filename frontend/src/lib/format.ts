import { format, formatDuration, parseISO, type Duration } from "date-fns";
import { tz } from "@date-fns/tz";

export const formatWhen = (iso: string | null | undefined, timeZone?: string) => {
  if (!iso) {
    return "–";
  }
  const pattern = "EEE MMM d, h:mm a";
  if (!timeZone) {
    return format(parseISO(iso), pattern);
  }
  return format(parseISO(iso), pattern, { in: tz(timeZone) });
};

export const formatDrive = (seconds: number | null | undefined) => {
  const whole = Math.max(0, Math.round(seconds || 0));
  let hours = Math.floor(whole / 3600);
  let minutes = Math.round((whole % 3600) / 60);
  if (minutes === 60) {
    hours += 1;
    minutes = 0;
  }
  const parts: Duration = {};
  if (hours) {
    parts.hours = hours;
  }
  if (minutes || !hours) {
    parts.minutes = minutes;
  }
  return formatDuration(parts);
};

export const formatMiles = (miles: number | null | undefined, digits = 0) => {
  if (miles === null || miles === undefined) {
    return "–";
  }
  return `${Number(miles).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  })} mi`;
};

export const formatInches = (value: number | null | undefined) => {
  if (value === null || value === undefined) {
    return "–";
  }
  return `${Number(value).toFixed(2)} in/hr`;
};

export const formatWind = (value: number | null | undefined) => {
  if (value === null || value === undefined) {
    return "–";
  }
  return `${Number(value).toFixed(0)} mph`;
};

export const defaultDeparture = () => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(8, 0, 0, 0);
  return format(tomorrow, "yyyy-MM-dd'T'HH:mm");
};
