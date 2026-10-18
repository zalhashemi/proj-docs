---
title: Quick Start
subtitle: "Trailmate"
version: 1.0.0
date: "2026-10-18"
author: "Trailmate team"
project: "Trailmate"
doc_id: quick-start
confidential: false
---

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

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| Q1 | Store links for iOS and Android | open question | not in repo | product owner |
