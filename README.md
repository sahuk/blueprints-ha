# blueprints-ha

Home Assistant blueprints. A monorepo that can hold several blueprints over
time; the first one covers **library opening hours for
[gotabiblioteken.se](https://www.gotabiblioteken.se/)** (the Götabiblioteken
consortium), served by the Axiell JSON API.

```
blueprints-ha/
├── blueprints/
│   └── template/
│       └── gotabiblioteken/
│           └── opening_hours.yaml     # the reusable per-library sensor blueprint
├── packages/
│   └── gotabiblioteken_opening_hours.yaml  # REST sensor that polls the API
└── README.md
```

## How it fits together

A Home Assistant blueprint can only be an automation, a script, or a template
entity — **none of these can make an HTTP request**. So the integration is two
halves:

1. **`packages/gotabiblioteken_opening_hours.yaml`** — a `rest` sensor that
   polls the API once an hour and stores the whole response in a `dates`
   attribute. This is the "subscribe to the API" half (installed once).
2. **`blueprints/template/gotabiblioteken/opening_hours.yaml`** — the reusable
   blueprint. Instantiate it **once per favorite library**; each instance reads
   the `dates` attribute and produces a tidy "opening hours today" sensor for
   that branch.

## Installation

### 1. Add the REST source sensor

Enable packages (once) in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Copy `packages/gotabiblioteken_opening_hours.yaml` into your
`<config>/packages/` directory and restart Home Assistant. You should now have
a `sensor.gotabiblioteken_oppettider_radata` entity whose attributes include a
`dates` list.

### 2. Import the blueprint

In Home Assistant: **Settings → Automations & scenes → Blueprints → Import
blueprint**, and paste:

```
https://github.com/sahuk/blueprints-ha/blob/master/blueprints/template/gotabiblioteken/opening_hours.yaml
```

Or drop the file manually into
`<config>/blueprints/template/gotabiblioteken/opening_hours.yaml`.

### 3. Pick your favorites (one sensor per library)

Create a template entity from the blueprint for **each** library you care
about. In `configuration.yaml` (or a package):

```yaml
template:
  - use_blueprint:
      path: gotabiblioteken/opening_hours.yaml
      input:
        branch_name: Linköpings huvudbibliotek
    name: Öppettider Linköpings huvudbibliotek
    unique_id: oppettider_linkopings_huvudbibliotek

  - use_blueprint:
      path: gotabiblioteken/opening_hours.yaml
      input:
        branch_name: Motala bibliotek
    name: Öppettider Motala bibliotek
    unique_id: oppettider_motala_bibliotek
```

(The same thing can be done entirely in the UI via **Settings → Devices &
services → Helpers → Create helper → Template**, choosing this blueprint.)

`source_sensor` defaults to `sensor.gotabiblioteken_oppettider_radata`, so you
only need to set `branch_name`. Set `include_self_service: false` on an
instance if you don't want Meröppet hours to count as "open".

## What each sensor gives you

State: today's staffed hours as a short string, e.g. `10:00–13:00, 14:00–19:00`
(or the self-service hours if the branch is self-service only, or `Stängt`).

Attributes:

| Attribute              | Example                                             |
| ---------------------- | --------------------------------------------------- |
| `branch`               | `Linköpings huvudbibliotek`                         |
| `date` / `date_label`  | `2026-10-20` / `Måndag 20 oktober`                  |
| `weekday`              | `Måndag`                                            |
| `open_now`             | `true`                                              |
| `status`               | `staffed` \| `self_service` \| `closed`             |
| `staffed_summary`      | `10:00–13:00, 14:00–19:00`                          |
| `self_service_summary` | `07:00–22:00` or `Stängt`                           |
| `shifts`               | list of `{type, service_type, info, from, to}`      |
| `hours_markdown`       | pre-formatted block for a Markdown card             |

`shifts` is the structured source of truth — it keeps **every shift** for the
day and distinguishes `Bemannat` (staffed) from `Meröppet` (self-service), so
split days and mixed service types are all preserved.

## Dashboard cards

**One card for all favorites** (built-in Markdown card, no custom components):

```yaml
type: markdown
title: Öppettider idag
content: |
  {% for e in [
    'sensor.oppettider_linkopings_huvudbibliotek',
    'sensor.oppettider_motala_bibliotek'
  ] %}
  {{ state_attr(e, 'hours_markdown') }}

  {% endfor %}
```

**A single library:**

```yaml
type: markdown
content: "{{ state_attr('sensor.oppettider_motala_bibliotek', 'hours_markdown') }}"
```

**At a glance** (built-in Entities card — state shows today's hours):

```yaml
type: entities
title: Bibliotek
entities:
  - sensor.oppettider_linkopings_huvudbibliotek
  - sensor.oppettider_motala_bibliotek
```

## Branch names

Use these exactly as `branch_name` (matching ignores surrounding spaces and
case):

- Berga bibliotek
- Bibliotek Agora
- Borensbergs bibliotek
- Borghamns bibliotek
- Boxholms bibliotek
- Ekholmens bibliotek
- Eneby bibliotek
- Finspångs huvudbibliotek
- Hageby bibliotek
- Horns bibliotek
- Johannelunds bibliotek
- Kisa bibliotek
- Krokeks bibliotek
- Lambohovs bibliotek
- Linghems bibliotek
- Linköpings huvudbibliotek
- Ljungsbro bibliotek
- Mantorps bibliotek
- Mjölby bibliotek
- Mogata bibliotek
- Motala bibliotek
- Norrköpings stadsbibliotek
- Rejmyre bibliotek
- Ringarums bibliotek
- Ryds bibliotek
- Skänninge bibliotek
- Skärblacka bibliotek
- Stinsen
- Sturefors bibliotek
- Tjällmo bibliotek
- Tranås stadsbibliotek
- Vadstena bibliotek
- Valdemarsviks bibliotek
- Väderstads bibliotek
- Ydre kommunbibliotek
- Åtvidabergs bibliotek
- Ödeshögs bibliotek
- Östra Husby bibliotek
- Östra Ryds bibliotek

## API notes

Endpoint:

```
https://api.axiell.com/openinghours/customers/637ce8087143292d469b8c9b/openinghours?locale=sv_SE&daysFromNow=0&numOfDays=2
```

Response shape:

```json
{
  "dates": [
    {
      "date": "2026-10-20",
      "branches": [
        {
          "branchName": "Borensbergs bibliotek",
          "openingHours": [
            { "serviceType": "Staffed",     "info": null,       "from": "09:00", "to": "14:00", "openingHoursType": "Regular" },
            { "serviceType": "SelfService", "info": "Meröppet", "from": "14:00", "to": "21:00", "openingHoursType": "Regular" }
          ]
        }
      ]
    }
  ]
}
```

An empty `openingHours` array means the branch is closed that day.
