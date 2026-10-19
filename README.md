# Route check

A TypeScript React and Django app that compares up to three truck routes. It samples the weather along each route at the truck's estimated arrival time, scores that weather against the load weight, and recommends the route with the least weather trouble and the shortest drive.

## Run it locally

You need Python 3.12, Node 22, and a free [Stadia Maps](https://client.stadiamaps.com/signup/) API key. Weather comes from [Open-Meteo](https://open-meteo.com/en/docs) and does not need a key.

```bash
cp .env.example .env
# put the Stadia key in STADIA_API_KEY

python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

If `python3 -m venv` says `ensurepip` is missing, install `python3.12-venv` and run that command again.

```bash
cd frontend
npm install
```

Two terminals:

```bash
cd backend
python manage.py test
python manage.py runserver
```

```bash
cd frontend
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to Django on port 8000.

Departure time is local time at the origin. The page says which timezone that is after a search.

## Routes worth trying

Two trips show the two things the page is for. Type the city and state. `Santa Fe, NM` has to include the S. `anta Fe` geocodes to a town in China, and the router rejects that path.

**Three routes, quiet weather.** Chicago, IL to Joliet, IL. Depart October 21, 2026 at 8:00 AM. Load 35,000 lb. Sample every 25 miles.

The router returns three paths of about 44, 47, and 49 miles. Risk is low on all of them, so the recommended card is the shortest drive. One of the longer cards is marked for tolls. This is the trip to use when you want to see Route A, B, and C on the map.

**One route, high rain.** Albuquerque, NM to Santa Fe, NM. Depart October 22, 2026 at 11:00 PM. Load 35,000 lb. Sample every 10 miles.

This is about 60 miles and one hour on I-25, so the router returns a single line and the page says so. Checked against the forecast for that departure, the middle of the drive is high rain (about 0.26–0.35 in/hr) for roughly 40 miles, with about 10 miles moderate and the rest low. Wind stays under 10 mph, so the checkpoint color is from rain. Open a checkpoint and read the rain number next to the level.

The forecast moves. If that night is dry when you try it, the same form still shows how a short trip is sampled. A longer haul such as Chicago, IL to Denver, CO, departing October 21, 2026 at 8:00 AM, is the other useful search: three routes across a full day, with the slider covering the corridor after they are drawn.

## How the code is split

The UI is grouped by what is on screen.

- `frontend/src/app` holds the screen and its state.
- `frontend/src/features/trip` is the form.
- `frontend/src/features/routes` is the route cards and checkpoints.
- `frontend/src/features/map` is the map, legend, and forecast slider.
- `frontend/src/domain` is the plan shape and the risk labels.
- `frontend/src/lib` is the API client and the date formatting.

The server stays one Django app. `planner/input.py` is the only place that reads the JSON body. `planner/services/plan.py` turns an already-checked trip into routes. Views translate that into HTTP status codes and do not catch a `PlanError` by printing it raw from a library.

A trip is not stored. There is no login and no queue, because the work is one read of Stadia and Open-Meteo. The Docker process is a single worker with a few threads: the wait is network, and the free host is small. A second machine would not share anything.

`POST /api/plan/` accepts JSON only, and only a few kilobytes. Place names are length-capped before they are sent to the geocoder. With `DJANGO_DEBUG=false` the process refuses the sample secret, redirects HTTP to HTTPS, and sets the usual cookie and HSTS flags. The browser still receives the Stadia key, because map tiles load from Stadia directly. Restrict that key by domain in the Stadia dashboard. It cannot read a database. There isn't one.

## What the request does

`POST /api/plan/` takes:

```json
{
  "origin": "Chicago, IL",
  "destination": "Denver, CO",
  "departure": "2026-10-21T08:00",
  "load_weight_lb": 35000,
  "sample_miles": 25
}
```

`sample_miles` is 10, 25, or 50.

The server geocodes both ends, asks Valhalla (through Stadia) for a truck route plus two alternates, and walks each route. Maneuver time is spread along the shape, so a checkpoint's ETA is the arrival time at that mile, not the departure time. Open-Meteo then returns wind (mph), rain plus showers (inches per hour), and snowfall (inches per hour) for that hour.

Load weight is only used in the risk rules. The router gets a normal tractor-trailer size, not the cargo weight.

If the router returns one or two routes, the page says so. It does not invent a third line.

## Risk rules

Checkpoint level is the worst of wind, rain, and snow. Where a printed range shares an edge (rain at 0.25 and 0.50, snow at 1.0, 2.0, and 3.0), the worse level is used. Rain at 1.00 in/hr is still severe. Snow at 3.0 in/hr is still severe. Wind at 55 mph is no travel.

| | Low | Moderate | High | Severe | No travel |
| --- | --- | --- | --- | --- | --- |
| Wind (mph) | <25 | 25–34 | 35–44 | 45–54 | ≥55 |
| Rain (in/hr) | <0.10 | 0.10–0.25 | 0.25–0.50 | 0.50–1.00 | >1.00 |
| Snow (in/hr) | <0.5 | 0.5–1.0 | 1.0–2.0 | 2.0–3.0 | >3.0 |

Load changes wind only:

- 55 mph or more is no travel for any load
- 45–54 mph and more than 30,000 lb is no travel (otherwise severe)
- 35–44 mph and more than 40,000 lb is severe (otherwise high)

Each checkpoint owns the miles since the previous one, scored with the weather at its ETA. The origin marker owns 0 miles. A short last stretch to the destination is included.

Average risk is the mile-weighted score: low 1, moderate 2, high 3, severe 4, no travel 5. Miles with no forecast are left out of the average.

## How a route is picked

Best first:

1. Fewest no-travel miles
2. Fewest severe miles
3. Fewest high miles
4. Lowest average risk
5. Shortest travel time

No-travel miles are not in the written list. They are compared first because a blocked stretch is worse than a severe one. The four written rules still break ties. The route cards show blocked, severe, and high miles, the average, and the drive time in that order.

Route A is the router's first path. Route B and Route C are alternates. The recommended card is not always Route A.

## Heatmap

The corridor is points along the routes plus a point about 16 miles to either side. One weather response covers every corridor point for the next 49 hours. The slider only changes which of those hours is drawn. It does not call the server again.

## Deploy

The hosted app is one [Render](https://render.com) web service. Django serves the API and the built React app, so there is a single URL.

1. Push this repo to GitHub. Do not commit `.env` or `keys.txt`.
2. In Render, create a Blueprint from `render.yaml`, or a new Docker web service pointed at this repo.
3. Set `STADIA_API_KEY` in the Render environment before the first deploy. Render generates `DJANGO_SECRET_KEY`.
4. In the Stadia dashboard, allow the Render domain (and `localhost:5173` for local work) if tiles do not load. The browser asks Django for the map key, then loads tiles directly from Stadia.
5. Free instances sleep after about 15 minutes. Open the URL a minute before a walkthrough.

## Walkthrough outline

About six minutes:

1. Run Chicago, IL to Joliet, IL (October 21, 2026, 8:00 AM, 35,000 lb, every 25 miles). Show the three lines. The recommended card is the shortest, because the weather is low on all of them.
2. Run Albuquerque, NM to Santa Fe, NM (October 22, 2026, 11:00 PM, 35,000 lb, every 10 miles). Open a high checkpoint and read the ETA, wind, rain, and snow. The level is rain.
3. Show why a card wins: blocked miles, then severe, then high, then average, then time.
4. Drag the 0–48 hour slider. The heat redraws without a new request.
