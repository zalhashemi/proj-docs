---
title: User Guide
subtitle: "BrightCart"
version: 1.0.0
date: "2026-10-18"
author: "BrightCart team"
project: "BrightCart"
doc_id: user-guide
confidential: false
---

BrightCart is an online shop for independent makers. This guide shows shoppers how to find a
product and pay for it.

## Getting started

Open BrightCart in any modern browser. The production address isn't recorded in the repository ⟨assumption⟩.
You don't need an account to browse.

## Tasks

### Browse products

1. Open the home page. The heading reads **Fresh from the makers**.
2. Each product appears as a card with its name and price, for example **Ceramic mug, $24**.

> [!TIP]
> Product cards show the price in dollars (`src/components/ProductCard.tsx`).

### Pay for your order

1. Go to the **checkout** page (`/checkout`).
2. Select **Pay now**.

> [!WARNING]
> In this version, **Pay now** does not start a payment yet. The button has no action attached
> (`src/pages/Checkout.tsx`), so no money is taken.

## Account and settings

BrightCart has no sign-in, profile or settings pages in this version.

## Troubleshooting

| Problem | What to do |
|---|---|
| The page is blank after refreshing | Reload the home page. The site serves every address from the same page (`vercel.json`) |
| Checkout shows an error in the browser console | The payment key is missing; contact the BrightCart team |

## Related documents

[Quick Start](quick-start.md) · [Troubleshooting and FAQ](troubleshooting-faq.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | Production URL | assumption | not in repo | product owner |
| Q1 | When will Pay now take payments? | open question | handler not implemented | product owner |
| Q2 | Will shoppers get accounts or order history? | open question | no such pages in repo | product owner |
