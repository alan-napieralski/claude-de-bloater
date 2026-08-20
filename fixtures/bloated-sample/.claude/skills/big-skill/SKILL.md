---
name: order-fulfilment
description: Handles order fulfilment tasks for the Acme storefront, including looking up orders, processing refunds, generating shipping labels, and drafting customer communications. Use when the user needs to fulfil, refund, ship, or communicate about a customer order.
tools: Read, Grep, Glob, Bash
---

# Order fulfilment

This skill handles the full order fulfilment lifecycle for the Acme storefront.

## Looking up an order

Orders are stored in the `orders` table, keyed by a UUID order ID. To look up an order, query by ID,
by customer email, or by the last four digits of the payment card plus the order date. Every order
has a status: `pending`, `paid`, `fulfilled`, `shipped`, `delivered`, `refunded`, or `cancelled`.
Status transitions are one-directional except `refunded` and `cancelled`, which can be reached from
`paid` or `fulfilled`. Never transition an order backwards (for example from `shipped` to `paid`)
without an explicit override flag, since downstream systems assume forward-only progress.

When a customer disputes an order, always check the audit log table first, every status transition
is recorded there with a timestamp and the actor who made it, before assuming the order record itself
is wrong.

## Processing a refund

A refund can be full or partial. A full refund reverses the entire payment and sets the order status
to `refunded`. A partial refund reverses only a specified amount and leaves the order in its current
status, only adding a note. Always check whether the order has already shipped before processing a
refund, a shipped order needs a return label generated as part of the refund flow, an unshipped order
does not.

Refunds over $500 require a second approval, recorded as a separate row in the `refund_approvals`
table, before the refund is actually issued to the payment processor. Never issue a refund over $500
without confirming that approval row exists.

Refund reason codes are: `customer_changed_mind`, `item_not_as_described`, `item_damaged`,
`item_never_arrived`, `duplicate_order`, `price_match`, `goodwill`. Always record a reason code, an
order without one fails the monthly finance reconciliation job.

## Generating a shipping label

Shipping labels are generated through the carrier API, keyed by the order's shipping address and
package weight. Package weight is estimated from the sum of each line item's weight, stored on the
product record, plus a fixed packaging weight of 150 grams. If a line item is missing a weight, do
not guess, flag it and ask a human to weigh the item before a label can be generated.

International orders need a customs form generated alongside the label, using the HS tariff code
stored on each product. An order missing an HS code for any international line item cannot get a
label until that code is filled in.

Once a label is generated, the order status moves to `shipped` automatically, and a shipping
confirmation email is queued. Do not move the status manually in this case, generating the label is
what triggers it.

## Drafting customer communications

Customer communications should always be polite, concise, and specific about what is happening next.
Never apologise excessively or use hedging language. State the fact, then the next step.

For a delayed order, the template is: acknowledge the delay, give a concrete new estimate if one is
available, and offer a small goodwill gesture (store credit, not a refund) if the delay exceeds seven
days from the original estimate.

For a damaged item, the template is: apologise once, ask for a photo if one has not already been
provided, and offer a replacement before a refund, replacements resolve the underlying complaint
better than a refund alone.

For an item that never arrived, the template is: confirm the tracking shows no delivery scan within
48 hours of the carrier's estimate, then offer a reship or refund, customer's choice, do not decide
for them.

## Edge cases

A cancelled order that was already partially fulfilled (some items packed, not yet shipped) needs the
warehouse notified separately, through the `warehouse_notifications` queue, not just a status change
in the orders table, or the warehouse will ship it anyway.

An order paid with a gift card that is later refunded should refund back to a new gift card, not the
original payment method, since gift cards cannot be reversed once redeemed.

A subscription order (recurring) that is refunded should also cancel the next scheduled charge, check
the `subscriptions` table for a linked subscription ID on the order before considering a refund
complete.
