# Style guide

Detailed styling conventions for the storefront frontend. This file only matters when someone is
actually touching CSS, markup, or component styling, not for backend routes, tests, or tooling.

## Colour tokens

All colour decisions live in `src/css/theme/colors.css`, in two layers:

- The palette layer (`--color-blue-500`, `--color-neutral-100`, `--color-black`) holds raw values.
  Nothing outside this file should reference the palette layer directly.
- The semantic layer (`--color-surface-primary`, `--color-surface-secondary`,
  `--color-button-primary`, `--color-button-secondary`, `--color-border-keyline`,
  `--color-text-primary`, `--color-text-muted`) points at the palette layer, and is the only layer
  markup ever uses.

To retheme the storefront, change the palette values and re-point the semantic tokens. No component
should need touching.

Never write a raw hex value, an `rgb()`/`rgba()` literal, or a Tailwind palette utility
(`bg-blue-500`, `text-neutral-800`) directly in a component. Always go through a semantic class:
`bg-surface-primary`, `text-text-primary`, `border-border-keyline`.

## Spacing scale

Spacing follows a fluid scale defined in `src/css/theme/scale.css`: `p-fl-xs` through `p-fl-2xl`,
plus matching `gap-fl-*` and `m-fl-*` variants. Pick a step on the scale rather than a hand-set
pixel or rem value. The scale is fluid (it interpolates between a minimum and maximum viewport
width), so a single step already covers small and large screens without a separate breakpoint
override in the common case.

Do not mix the fluid scale with fixed Tailwind spacing utilities (`p-4`, `gap-6`) in the same
component. Pick one system per component and stay consistent within it.

## Typography

Headings use the display typeface, body copy uses the text typeface, both loaded via
`src/css/theme/fonts.css`. Type sizes come from the same fluid scale as spacing:
`text-fl-xs` through `text-fl-4xl`. Line height and letter spacing are set per size step and should
not be overridden per component.

Headings should carry `text-wrap: balance` where the browser supports it, so a heading never breaks
after a single short word on its own line.

## Buttons

The button atom lives in `src/css/components/button/button.css` and is used as
`.c-button.c-button--primary` or `.c-button.c-button--secondary`. Do not restyle a button with
inline utilities, if a new visual variant is genuinely needed, add it to the button component's own
CSS file as a new modifier class.

Every button needs a visible focus state and, if it triggers an async action, a disabled state while
that action is in flight. A button that only communicates state through colour must also change
shape, icon, or text, never colour alone.

## Forms

Form fields share a base class, `.c-field`, with modifiers for state: `.c-field--error`,
`.c-field--disabled`. Error state always pairs a red accent with a visible text message below the
field, describing what to fix, never colour alone.

Labels are always visible, never placeholder-only. A placeholder may supplement a label with an
example value, never replace it.

## Cards

The product card component (`src/css/components/product-card/product-card.css`) is the single
source of truth for how a product is presented anywhere in the storefront: the catalogue grid, search
results, and the "related products" rail all reuse it rather than each defining their own card
styling. If a listing context genuinely needs a different layout, extend the card component with a
new modifier rather than writing parallel CSS elsewhere.

## Icons

Icons are served from a single SVG sprite, referenced as
`<svg class="c-icon c-icon--md"><use href="/sprite.svg#icon-name" /></svg>`. Never inline raw SVG
path data directly in markup, and never reach for an icon font. New icons get added to the sprite
source under `src/img/icons/` and are rebuilt automatically.

## Responsive breakpoints

Breakpoints are defined once, in `src/js/config/breakpoints.config.js`, and wired into the Tailwind
config from there. Anything in JS that needs a breakpoint value imports it from that file rather than
hard-coding a pixel number, so the two never drift apart.

## Animation

Prefer CSS transitions and animations over JavaScript animation loops wherever the effect can be
expressed declaratively. Any animation beyond a simple fade or slide must be gated behind
`prefers-reduced-motion`, checked via the `useReducedMotion` composable rather than a raw media query
scattered through component code.

## Dark mode

Dark mode is driven by a `data-theme` attribute on the document root, never a class toggled by
JavaScript alone, so the correct theme can be set before first paint from a stored preference.
Every semantic colour token has a dark-mode value defined alongside its light-mode value in the same
file, there is no separate dark-mode stylesheet to keep in sync.

## Component folder structure

Every component's CSS lives in its own folder under `src/css/components/<name>/`, one file per
component, never several unrelated components sharing one file. This mirrors the JS component
structure and keeps a component's styling, markup, and behaviour easy to find together even though
they live in different file types.

## Naming

Custom classes follow flat BEM: `.block__element` and `.block--modifier` as standalone selectors,
never written as nested `&__element`/`&--modifier` inside a parent rule, since the nested form is not
greppable and obscures the generated selector.
