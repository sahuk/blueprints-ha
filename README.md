# blueprints-ha

Home Assistant tooling for **library opening hours** from
[gotabiblioteken.se](https://www.gotabiblioteken.se/) (the Götabiblioteken
consortium), served by the Axiell JSON API.

Two ways to use it — pick one:

| | [Custom integration](#custom-integration-gui-recommended) | [Template blueprint](#template-blueprint-yaml-alternative) |
|---|---|---|
| Setup | GUI, no YAML | YAML (`configuration.yaml`) |
| Pick libraries | multi-select dropdown | one `use_blueprint` per library |
| Polls the API | itself | needs a separate REST sensor |

The integration is the recommended path. The blueprint is kept as a
YAML-only alternative (template blueprints can't be created from the GUI, which
is why the integration exists).

---

## Custom integration (GUI, recommended)

A proper config-flow integration: install once, then pick your favorite
libraries from a dropdown. It polls the API itself (every 3 hours) and creates
one "opening hours today" sensor per favorite. No YAML at all.

### Install

**Via HACS (custom repository):**

1. HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/sahuk/blueprints-ha` with category **Integration**.
3. Install **Götabiblioteken opening hours**, then restart Home Assistant.

**Manually:** copy `custom_components/gotabiblioteken/` into your
`<config>/custom_components/` directory and restart.

### Configure

**Settings → Devices & services → + Add integration → Götabiblioteken.**
Select your favorite libraries in the multi-select, choose whether Meröppet
(self-service) counts as open, and submit. Change favorites any time via the
integration's **Configure** button.

Each favorite becomes a `sensor.oppettider_<library>` entity.

---

## Template blueprint (YAML, alternative)

```
blueprints/template/gotabiblioteken/opening_hours.yaml   # the reusable sensor recipe
packages/gotabiblioteken_opening_hours.yaml              # REST sensor that polls the API
```

Because a template blueprint can't make HTTP requests, this path has two parts:
a REST sensor (installed once) that stores the API payload in a `dates`
attribute, and the blueprint that turns it into a per-library sensor.

### 1. Add the REST source sensor

Enable packages (once) in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Copy `packages/gotabiblioteken_opening_hours.yaml` into `<config>/packages/`
and restart. You'll get `sensor.gotabiblioteken_oppettider_radata`.

### 2. Import the blueprint

**Settings → Automations & scenes → Blueprints → Import blueprint**, and paste:

```
https://github.com/sahuk/blueprints-ha/blob/master/blueprints/template/gotabiblioteken/opening_hours.yaml
```

### 3. Create one sensor per favorite

```yaml
template:
  - use_blueprint:
      path: gotabiblioteken/opening_hours.yaml
      input:
        branch_name: Linköpings huvudbibliotek
    name: Öppettider Linköpings huvudbibliotek
    unique_id: oppettider_linkopings_huvudbibliotek
```

`branch_name` must match a name from [the list below](#branch-names).

---

## What each sensor gives you

Both paths produce the same thing. State: today's staffed hours as a short
string, e.g. `10:00–13:00, 14:00–19:00` (or the self-service hours if the
branch is self-service only, or `Stängt`).

Attributes:

| Attribute              | Example                                             |
| ---------------------- | --------------------------------------------------- |
| `branch`               | `Linköpings huvudbibliotek`                         |
| `date` / `date_label`  | `2026-10-20` / `Tisdag 20 oktober`                  |
| `weekday`              | `Tisdag`                                            |
| `open_now`             | `true`                                              |
| `status`               | `staffed` \| `self_service` \| `closed`             |
| `staffed_summary`      | `10:00–13:00, 14:00–19:00`                          |
| `self_service_summary` | `07:00–22:00` or `Stängt`                           |
| `shifts`               | list of `{type, service_type, info, from, to}`      |
| `hours_markdown`       | pre-formatted block for a Markdown card             |

`shifts` keeps **every shift** for the day and distinguishes `Bemannat`
(staffed) from `Meröppet` (self-service), so split days and mixed service types
are all preserved. `open_now` recomputes locally every minute; the API itself
is only polled every 3 hours.

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

**At a glance** (built-in Entities card — state shows today's hours):

```yaml
type: entities
title: Bibliotek
entities:
  - sensor.oppettider_linkopings_huvudbibliotek
  - sensor.oppettider_motala_bibliotek
```

## Branch names

Only needed for the blueprint path (the integration shows these in a dropdown).
Matching ignores surrounding spaces and case:

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

(Some branches are omitted by the API on days they're closed, so a single day
shows ~40; the full roster is ~46.)

## API notes

```
https://api.axiell.com/openinghours/customers/637ce8087143292d469b8c9b/openinghours?locale=sv_SE&daysFromNow=0&numOfDays=2
```

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

An empty `openingHours` array means the branch is closed that day. The customer
id `637ce8087143292d469b8c9b` is Götabiblioteken's.
