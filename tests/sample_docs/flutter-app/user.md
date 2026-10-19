---
title: User Pack
subtitle: Trailmate
version: 1.0.0
date: '2026-10-18'
author: Trailmate team
project: Trailmate
pack: user
chapters:
- quick-start
- release-notes
confidential: false
---

# Quick Start {#ch-quick-start}

## 1. Install the app

Trailmate is a Flutter app for iOS and Android (`pubspec.yaml`, `android/`). To run it from source:

```bash
flutter pub get
flutter run
```

## 2. Open your trails

The app opens on **Your trails** (`lib/screens/home_screen.dart`). Until you add a trail, it
shows **Plan your first hike**.

## 3. Create a trail

Tap **New trail** in the bottom-right corner.

> [!NOTE]
> In this version the **New trail** button has no action yet (`onPressed: () {}`).

## 4. Next steps

See the [User Guide](user-guide.md).

# Release Notes {#ch-release-notes}

## 2.1.0 (build 21)

The version comes from `pubspec.yaml` (`version: 2.1.0+21`).

> [!NOTE]
> The project has no CHANGELOG, git history or tags, so this release can't be broken down
> into changes. Add a `CHANGELOG.md` or tag releases to get detailed notes here.

# Assumptions and open questions {#ch-assumptions}

Not included: Upgrade and Migration Guide, User Guide, Admin Guide, Onboarding Deck Outline (not selected for this sample).

| # | Chapter | Item | Type | Why unverified | Who can confirm |
|---|---|---|---|---|---|
| Q1 | Quick Start | Store links for iOS and Android | open question | not in repo | product owner |
| Q2 | Release Notes | What changed in 2.1.0? | open question | no history in repo | mobile lead |
