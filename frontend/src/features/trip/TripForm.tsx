import { useState, type FormEvent } from "react";
import { Else, If, Then } from "react-if";
import type { SampleMiles, TripRequest } from "@/domain/types";
import { defaultDeparture } from "@/lib/format";
import { fieldClass, FormField } from "./FormField";
import { PanelLabel } from "@/features/shell/PanelLabel";

const SPACINGS = [10, 25, 50] as const satisfies readonly SampleMiles[];

type TripFormProps = {
  loading: boolean;
  onSubmit: (form: TripRequest) => void;
};

export const TripForm = ({ loading, onSubmit }: TripFormProps) => {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [departure, setDeparture] = useState(defaultDeparture);
  const [loadWeight, setLoadWeight] = useState("35000");
  const [sampleMiles, setSampleMiles] = useState<SampleMiles>(25);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit({
      origin,
      destination,
      departure,
      load_weight_lb: Number(loadWeight),
      sample_miles: sampleMiles,
    });
  };

  return (
    <form className="flex flex-col gap-3.5 px-4 pt-4 pb-5" onSubmit={handleSubmit}>
      <PanelLabel title="Trip" />
      <FormField id="origin" label="Origin">
        <input
          id="origin"
          className={fieldClass}
          value={origin}
          placeholder="Chicago, IL"
          autoComplete="off"
          required
          onChange={(event) => setOrigin(event.target.value)}
        />
      </FormField>
      <FormField id="destination" label="Destination">
        <input
          id="destination"
          className={fieldClass}
          value={destination}
          placeholder="Denver, CO"
          autoComplete="off"
          required
          onChange={(event) => setDestination(event.target.value)}
        />
      </FormField>
      <FormField id="departure" label="Departure" hint="Local time at the origin.">
        <input
          id="departure"
          className={fieldClass}
          type="datetime-local"
          value={departure}
          required
          onChange={(event) => setDeparture(event.target.value)}
        />
      </FormField>
      <FormField id="load" label="Load weight (lb)">
        <input
          id="load"
          className={`${fieldClass} tabular-nums`}
          type="number"
          min="1"
          max="100000"
          step="1"
          value={loadWeight}
          required
          onChange={(event) => setLoadWeight(event.target.value)}
        />
      </FormField>
      <fieldset>
        <legend className="text-[13px] font-medium">Sample every</legend>
        <div className="mt-1.5 grid grid-cols-3 gap-1 rounded-lg bg-canvas p-1">
          {SPACINGS.map((miles) => (
            <label
              key={miles}
              className={`cursor-pointer rounded-md py-1.5 text-center text-sm transition focus-within:ring-2 focus-within:ring-accent ${sampleMiles === miles ? "bg-surface font-semibold text-ink shadow-sm" : "text-muted hover:text-ink"}`}
              htmlFor={`sample-${miles}`}
            >
              <input
                id={`sample-${miles}`}
                className="sr-only"
                type="radio"
                name="sample-miles"
                value={miles}
                checked={sampleMiles === miles}
                onChange={() => setSampleMiles(miles)}
              />
              {miles} mi
            </label>
          ))}
        </div>
      </fieldset>
      <button
        className="mt-1 h-11 rounded-lg bg-accent text-sm font-semibold text-white transition hover:bg-accent-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        disabled={loading}
        aria-busy={loading}
      >
        <If condition={loading}>
          <Then>Checking routes…</Then>
          <Else>Compare routes</Else>
        </If>
      </button>
    </form>
  );
};
