# Changelog

🇩🇪 [Deutsche Version](CHANGELOG.md)

All notable changes to PleasePrintit. Versions follow [Semantic Versioning](https://semver.org/), the prebuilt image is available at `ghcr.io/neodk2004/pleaseprintit`.

## [Unreleased]

### Added
- **“Open in slicer”:** buttons on a request open the 3D file directly in OrcaSlicer, Bambu Studio or Creality Print on your computer. Pick which buttons appear under Settings → Workshop. The slicer fetches the file via a signed link that is valid for one hour.

## [1.1.0] – 2026-11-07

### Added
- **Archive with search:** printed and rejected requests move to the archive after a configurable period (default 14 days, 0 = button only) or with a button, several at once. Search by title, file, friend and date range. Friends don't notice any of this.
- **Statistics:** requests, grams and material cost per month, popular filaments and colors, waiting time and rejection reasons for you. Every friend sees their own numbers on their profile.
- **Tip button:** your own link (PayPal.me, Ko-fi …) shows up on printed requests. The app itself handles no money.
- **STEP files** from CAD programs with 3D preview, dimensions and volume, read right in the browser.

### Changed
- Settings split into four tabs: printer, filaments, workshop, legal.
- New filaments are picked from a fixed list of 14 types with the density pre-filled, instead of free text.

### Fixed
- Rejected requests with a reason could not be opened in the workshop view (error 500).

### Security
- The STEP reader (occt-import-js 0.0.23, LGPL-2.1) runs isolated in a Web Worker. Only there is `eval` allowed, all pages stay without it.

## [1.0.0] – 2026-11-07

First self-hosting release.

### Features
- **Requests by link or file:** a link to Printables, MakerWorld or Thingiverse (title and preview image are fetched) or your own STL or 3MF file.
- **3D preview in the browser** with dimensions and a check whether the model fits your build plate.
- **Filaments and colors** from your stock, or “Random”. Add a price per kg to get a material cost estimate.
- **“Printed for you”:** parts, weight and material cost per friend on their profile and in the friends list.
- **Clear status:** submitted → planned → printed, or rejected with a reason. Optional e-mail notifications.
- **Invite only:** invite links are valid for 7 days and can be used once. Accounts can be disabled, “forgot password” works via e-mail.
- **Fair limits:** at most 10 open requests and 500 MB of 3D files per person.
- **German, English, French** for the whole app, e-mails always in the recipient's language.
- **Mobile friendly:** installable on the home screen (PWA), light and dark theme.
- **Legal notice and privacy page** built in, unreadable for address scrapers.
- **Runs almost anywhere:** prebuilt image for x86 and ARM64 (including Raspberry Pi 4/5), SQLite instead of a database server, about 50 MB of RAM.
- **Daily backups** with a verification tool, the last 14 are kept.
- **Secure by default:** SSRF protection when fetching previews, CSP and HSTS headers, brute-force throttling on logins, container without extra privileges and with a read-only file system.

### Project
- Install with Docker Compose or Dockhand, instructions in German and English.
- Tests, compose validation and a Docker test run via GitHub Actions, Dependabot for dependencies.
- MIT license, `SECURITY.md`, issue templates and `AGENTS.md`.

[Unreleased]: https://github.com/neodk2004/pleaseprintit/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/neodk2004/pleaseprintit/releases/tag/v1.0.0
