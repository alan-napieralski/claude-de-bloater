# Styling conventions

Detailed styling conventions for the Fintrack dashboard. Only relevant when touching CSS or component markup.

## Colour

All colour decisions live in `src/css/theme/colors.css`, in two layers: a palette layer of raw values, and a semantic layer (`bg-surface-primary`, `text-surface-muted`, `border-keyline`) that markup actually uses. Never reference the palette layer from a component.

## Spacing and type

Both come from a fluid scale (`p-fl-*`, `text-fl-*`), defined in `src/css/theme/scale.css`. Pick a step on the scale rather than a hand-set value.

## Charts

Every chart (spending over time, category breakdown, budget progress) shares one base config in `src/charts/base-config.js`. Colours for chart series come from a fixed, colour-blind-safe palette defined there, never picked ad hoc per chart.

## Cards and tables

The account-summary card and the transaction table are the two components every other view composes from. Extend them with modifiers rather than writing parallel components.

## Icons

Served from a single SVG sprite. Never inline raw SVG path data, never an icon font.

## Dark mode

Driven by a `data-theme` attribute on the document root, set before first paint from a stored preference. Every semantic token has a dark-mode value defined alongside its light-mode value.

## Naming

Custom classes follow flat BEM: `.block__element` and `.block--modifier` as standalone rules, never nested.
