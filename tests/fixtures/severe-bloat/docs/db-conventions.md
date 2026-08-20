@docs/backend.md

# Database conventions

Every table has a `created_at` and `updated_at` column, set by the database, never by application code. Foreign keys are always named `<singular_table>_id`. Migrations are one-directional, a rollback is a new forward migration, never an edit to an applied one.

See `docs/backend.md` for how services call into this layer.
