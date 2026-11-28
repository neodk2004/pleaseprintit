# Changelog

🇩🇪 [Deutsche Version](CHANGELOG.md)

All notable changes to PleasePrintit. Versions follow [Semantic Versioning](https://semver.org/), the prebuilt image is available at `ghcr.io/neodk2004/pleaseprintit`.

## [Unreleased]

## [1.8.0] – 2026-11-28

### Added
- **Your own look:** Under Settings → Workshop → Appearance you give your workshop its **own name** (up to 40 characters, shown in the header, browser tab and sign-in page) and pick one of nine **designs**, each with its own layout and in light and dark: **Workshop** (orange, as before), **Forest** (green, serif headings, soft corners), **Blueprint** (blue, sharp-edged, sidebar), **Glass** (frosted-glass bar, segmented tabs), **Aurora** (purple, tinted surfaces, navigation bar, at the bottom on phones), **Panel** (side menu with accent bar), **Terminal** (monospace, green, square), **Newspaper** (serifs, masthead, rules) and **Pop** (thick borders, hard shadows). Pure CSS, no new dependency.

- **Emails in your workshop’s look:** Status emails, emails about questions and the password email carry the **workshop name** in the header, in the footer (“You’re getting this email because you added an email address in *name*.”) and as the **sender name**. They also pick up the accent colour, font, corner radius and a logo in the colour of the chosen design. The **plain-text version** of every email contains the name and the footer too. Without a name of your own the emails look as before.

### Fixed
- **Order page with little room:** The right-hand column could grow to the edge of the screen, for example next to a sidebar. The columns now keep to their space.

## [1.7.2] – 2026-11-28

### Added
- **Change the title afterwards:** Each order has a new “Change title” card (friends on their own orders, the workshop on all of them). Handy when the preview does not work, e.g. with MakerWorld. Idea from maume86 (#17), thanks!
- **Image from the clipboard:** A copied image can be pasted straight in with Ctrl+V, on a new order and under “Replace preview image”. No need to save the image as a file first. The server checks type and size (up to 5 MB) as before.
- **GitHub link in the footer:** The workshop sees a short way to the project on GitHub at the bottom. Friends do not see it.

### Changed
- “Change title” and “Replace preview image” now sit right below the order details, so no more scrolling.

## [1.7.1] – 2026-11-27

### Changed
- **Tidier settings:** The long “Workshop” tab is split into three: “Workshop” (archive, currency, limit, pay in advance, tip), “Notifications” (mail, ntfy) and “Preview & slicer”. Saving returns to the right tab.

## [1.7.0] – 2026-11-27

### Added
- **Push notifications via ntfy:** The workshop can get a push notification on their phone for new print requests and questions, via ntfy.sh or a self-hosted ntfy server (home network works too). Set it up under Settings → Workshop → Push notification via ntfy: topic address, optional access token or user:password (stored encrypted, `NTFY_TOKEN` in `.env` takes precedence), a button for a test message, can be paused. Works without e-mail as well. No new dependency. Idea and groundwork by GhostService (PR #18), thank you!

## [1.6.2] – 2026-11-24

### Added
- **Preview for Thingiverse and Cults3D:** With your own free access (Thingiverse app token, Cults3D nickname with API key), the app gets title and image through their official APIs. Without access nothing changes. A short guide is in the README.
- **Access in the settings:** Under Settings → Workshop → Link preview you enter the access directly in the web interface, no Docker knowledge needed. It is stored **encrypted** (derived from `SECRET_KEY`) and never shown again. Variables in `.env` (`THINGIVERSE_TOKEN`, `CULTS3D_USER`, `CULTS3D_KEY`) still take precedence. New dependency: `cryptography`.

## [1.6.1] – 2026-11-24

### Fixed
- **Preview for Printables links:** Printables blocks fetching its web pages. Title and image now come through its API, so the preview works again.
- **MakerWorld:** The site still blocks automatic fetching. When submitting you can now **upload your own image** (collapsible under the link); the title comes from the title field. Automatic fetching will follow as soon as it becomes possible.

### Changed
- **Small images as WebP:** Preview images are scaled down to at most 800 pixels and stored as WebP (instead of originals of several MB). New dependency: Pillow.
- The fetcher identifies itself with its own honest name (`PleasePrintit-LinkPreview`).
- Code tidy-up (number inputs, money display).

## [1.6.0] – 2026-11-22

### Added
- **Selectable currency:** In Settings → Workshop you choose the currency (EUR, USD, GBP, CHF, CAD, AUD, SEK, NOK, DKK, PLN, CZK). Euro still shows “€”, all others show their code, e.g. “USD 12.50”. Nothing is converted.
- **Tidier status area:** The workshop now only sees the **next step** (Accept → Printed → On its way → Delivered). The tracking field only appears when it’s needed. “Decline” can be expanded. The free choice of all statuses is still there as “Change status freely (correction)”.

Thanks to @dexxfm for both ideas.

## [1.5.1] – 2026-11-22

### Fixed
- **Clear error messages:** Errors now show as a regular app page with a readable text and a button back to the overview, instead of a bare “Bad Request”. This includes invalid numbers for price, credit and surcharge, and an expired session.
- **Negotiating a price:** If the friend hasn’t answered an offer (or has no email), the workshop can now move on: **“Mark as agreed”** records a verbal agreement. Before, the order got stuck at “The price hasn’t been agreed yet”.

## [1.5.0] – 2026-11-22

### New
- **Shipping:** After “Printed” there are two new steps, **On its way** and **Delivered**, with a status email to the friend. When you set “On its way” you can enter a **tracking number or tracking link**. It appears in the email and on the request, and a link becomes clickable. Pick-ups keep the existing steps only.
- **Negotiate the price:** The workshop sends an offer, the friend accepts or makes a counteroffer, and the workshop accepts it or sends a new offer. Until the price is agreed, nothing is planned, printed or charged. Both sides get an email.
- **Adjustable open-request limit:** In Settings → Workshop you set how many requests a friend may have open at once. The default is now **50** instead of 10.
- **Status emails in the new design:** The progress bar in the emails now shows hexagons with the filament thread, like in the app, including the shipping steps.

Thanks to @dexxfm for the ideas on shipping and price negotiation.

## [1.4.0] – 2026-11-21

### Added
- **Pay in advance (optional):** under Settings → Workshop choose the mode: off, **tick per request** or **credit account**. It is switched on per friend on the Friends page. The price is filament cost plus a percentage surcharge (default 30 %) for power, wear and failed prints; without volume or price per kg you set it on the request yourself.
  - Without payment a request cannot be set to “planned”.
  - With credit the app deducts when a request is submitted as soon as the balance is enough, and refunds rejected requests. Friends see balance and history on their profile.
  - The money changes hands outside the app (cash, PayPal); it only calculates and remembers the status.
- **New progress bar:** hexagons with a filament thread that gets thicker from step to step. The steps appear one after another with an animation.
- **Animated icons:** all icons move when you hover buttons, links and tabs. With “reduce motion” set in the system everything stays still.

### Security
- For STEP files the volume comes from the friend's browser. The price is never calculated from it; the workshop sets it.

## [1.3.0] – 2026-11-17

### Added
- **E-mail to the workshop on new requests:** enter your address under Settings → Workshop. Empty = no e-mails.
- **Questions on a request:** friend and workshop write to each other right on the request, and the other side gets an e-mail. No more “which size?” in the group chat.
- **Internal note:** a text field on each request that only the workshop sees, e.g. for print settings.
- **Position in the queue:** friends see “Position 3 in the queue”. Planned requests count before new ones.
- **Print again:** printed requests can be ordered again with one click. File, image and filament are copied.
- **Photo of the finished print:** the workshop uploads a photo. The friend sees it on the request and gets it attached to the “Printed” e-mail.
- **Pause e-mails:** friends (profile) and the workshop (settings) can turn e-mails off without deleting their address.

### Fixed
- gunicorn 27 logged `Control server error: Read-only file system` on startup. The unused control socket is now disabled (`--no-control-socket`).

### Security
- gunicorn 26.2.0 → 27.0.0 (stricter HTTP request validation).

## [1.2.0] – 2026-11-09

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

[Unreleased]: https://github.com/neodk2004/pleaseprintit/compare/v1.8.0...HEAD
[1.8.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.2...v1.8.0
[1.7.2]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.1...v1.7.2
[1.7.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.2...v1.7.0
[1.6.2]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/neodk2004/pleaseprintit/releases/tag/v1.0.0
