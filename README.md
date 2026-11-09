# Black Michael Collection — website source

A complete multi-page static website, with 23 built HTML pages, all CSS and JavaScript, editable content files, two SVG logo concepts, and a generated logo direction board.

## Start here

1. Extract the ZIP first. Open `START-HERE.html` for links to the website and logo concepts.
2. Open `dist/index.html` to browse the site locally. Links, search, filtering, sorting and the mobile menu work without a build.
3. For the owner editor to load JSON automatically, serve the site locally. From the project folder run `python3 -m http.server 8000 --directory dist`, then open `http://localhost:8000/owner-editor.html`. On Windows, use `py` instead of `python3` if needed. Alternatively, use the editor’s Import JSON button.

No Node installation or npm dependencies are needed. Python 3.10+ is needed only to rebuild. Keep Python installed on the build host.

## What you have

| File or folder | Purpose |
|---|---|
| `dist/` | Complete generated website, including every individual HTML page |
| `content/products.json` | Product descriptions, photos, availability, prices and checkout links |
| `content/events.json` | Confirmed vendor appearances; empty until you supply them |
| `content/posts.json` | Three editable starter blog articles; add as many as you like |
| `content/site.json` | Domain, preview mode, Instagram, email, editorial imagery and policies |
| `assets/site.css` | Layout, colors, typography and responsive styles |
| `assets/site.js` | Mobile menu, search, filtering, sorting and inquiry composer |
| `scripts/build.py` | Generates all pages and metadata from the content files |
| `scripts/check.py` | Checks generated links, assets, metadata and structured data |
| `dist/owner-editor.html` | Browser helper to edit and download content JSON |
| `dist/brand-concepts.html` | Two editable SVG logo directions |
| `assets/logo-directions.png` | Generated visual inspiration board; SVGs are simplified code-native interpretations |

The site includes Home, Shop, three category pages, six individual collection previews, About, Events, Journal, three article pages, Contact, FAQ, Policies, 404, a logo page and the owner helper. Every main destination is a separate HTML file with its own URL.

## Editing and publishing content

Edit the files in `content/`, not the copies inside `dist/content/`. You can edit JSON in GitHub directly or use `owner-editor.html` to load, edit, validate and download a replacement file. Upload replacement content files and photos to the repository, then commit. A Git-connected hosting service can rebuild on each commit.

The editor is a local file preparation tool, not a connected CMS. It has no account or authentication and cannot publish to GitHub. Do not put private notes, customer details, API keys or other secrets in it or anywhere in this static repository. Everything shipped in `dist/` is public if you deploy it.

Build and validate from the project root:

```sh
python3 scripts/build.py
python3 scripts/check.py
```

Rebuilding replaces `dist/`. If you edit generated HTML directly, your changes will disappear at the next build; make permanent layout/copy changes in `scripts/build.py`. The complete generated HTML is included for a developer who prefers to work directly with individual pages.

## Product setup

Each product has a unique lowercase `slug`, name, description, category, image, alt text, price, status, details, checkoutUrl and featured flag. Categories are `minerals`, `gemstones`, and `jewelry`. Status is `preview`, `available`, or `sold`. Price is a number in USD or `null` for price on request.

For each real listing:

1. Upload your original photo to `assets/`. Use a reasonably sized JPEG or WebP, ideally around 1200–1600 pixels on the long edge.
2. Set `image` to that file, for example `assets/red-beryl-specimen.jpg`, and write accurate alt text.
3. Replace the name, description and details with confirmed information. Include gemstone/mineral identity, dimensions, weight where relevant, condition, repairs, treatments, documentation and locality/origin information as appropriate. Clearly distinguish attributed locality from laboratory-determined origin.
4. Set the numeric price or leave `null` for an inquiry-only piece.
5. Set status to `available` or `sold` only after verification. `preview` products are excluded when production mode is enabled.
6. Add a provider-hosted HTTPS checkout URL to enable Buy securely. Without one, the visitor is directed to inquire.
7. Set `featured` to true for items you want on the homepage.

The screenshot supplied for inspiration is displayed through CSS crops in preview mode. These are not verified product identities, photographs suitable for a final catalog, or live inventory. No prices, origin claims, gemstone certification, testimonials or events were invented.

## Payments and inventory

This is a static storefront. It does not contain a cart, payment processor, order database, account system, shipping calculator, tax engine or automatic inventory sync. The Buy securely link takes a customer to a payment page you configure with a provider such as Stripe or Square.

Before enabling a payment link, set up the product and its checkout terms at your provider, including shipping, taxes and any quantity or payment limit. For one-of-a-kind pieces, use the provider’s inventory or payment-limit controls so a static listing cannot cause multiple sales. Test the full purchase flow in the provider’s test environment. After a sale, mark the product sold, disable its payment link and rebuild the site. A more advanced storefront can later connect to a commerce backend.

No live processor is connected and no transaction has been tested in this delivery. No payment keys belong in public code.

## Events

Add real events to `content/events.json`. The owner editor includes a template with fields for name, start/end time, timezone label, venue, street address, city/state, booth, admission details, organizer URL and description. Replace every template value.

Use ISO dates with UTC offsets, such as `2027-01-15T10:00:00-07:00`, and a matching human-readable timezone label. The end must be later than the start. Each event gets its own detail page and Event structured data. Upcoming and past appearances are separated at build time; rebuild after an event ends or arrange a scheduled build at your host. Dates do not update themselves on an unchanged static deployment.

## Blog and search visibility

The three starter articles are editable drafts for owner review. Add original knowledge, your own photography, specific examples and verified sourcing details to make the journal distinctive. Do not imply credentials, mine visits or first-hand experience you cannot substantiate.

New posts need a unique slug, title, description, category, YYYY-MM-DD publication date, sections (heading and text), and optional source links. Section text is plain text, not executable HTML. The article pages include bylines, publication dates and BlogPosting structured data.

Implemented foundations:

- Separate, pre-rendered pages: core content is readable without JavaScript.
- Unique page titles and descriptions, semantic headings and linked category/product/article pages.
- Organization and article structured data; Product/Offer data only for confirmed, non-preview products; Event data only for events you actually supply.
- Canonical URLs and an XML sitemap when you provide the domain.
- A preview noindex setting to keep unfinished listings out of search results.
- Small local scripts and system fonts; no third-party font or analytics requests.

Before launch, set your final domain in siteUrl and turn preview off. Submit the generated sitemap in Google Search Console and Bing Webmaster Tools. Keep business naming and contact details consistent across your site and public profiles. Write useful articles that answer real customer questions, and link them to relevant categories and products. Build national reach around product-specific searches and actual event appearances rather than invented city pages.

No technical feature guarantees a Google ranking, inclusion in AI answers or an AI recommendation. Google says its established SEO principles remain relevant to AI search features. The site does not depend on a special AI markup file.

## GitHub and hosting

Keep this project in a GitHub repository, but use an appropriate external host for the shop. GitHub Pages specifically prohibits free hosting of ecommerce sites and sites primarily facilitating commercial transactions.

For a Git-connected static host, such as Cloudflare Pages:

- Upload the **contents of this project folder** to the repository root.
- Framework preset: none/static.
- Build command: `python3 scripts/build.py && python3 scripts/check.py`
- Output/publish directory: `dist`
- Connect your custom domain in the hosting service.
- If the host rewrites `.html` URLs to extensionless URLs, align canonical and sitemap URLs with that behavior before launch. The included links use explicit `.html` paths for portability.

If you choose direct static upload instead, upload the contents of `dist/` to the site’s document root. Keep `assets/` beside the HTML files. The files are portable; they do not require Sites hosting.

The complete source is in the ykanaras/blackmichaelcollection GitHub repository. No hosting account has been connected and no public storefront has been deployed.

## Launch checklist

- Confirm the business name, Salt Lake City location and Instagram handle taken from your reference.
- Add original product and editorial photos. Replace preview screenshot imagery throughout.
- Confirm products, descriptions, prices, stock and disclosures.
- Review the three starter articles and their publication dates.
- Enter real appearances, or leave the Events page’s honest empty state.
- Add your public business email if you want the inquiry form to open an email draft; otherwise it prepares a message to paste into Instagram. It never silently sends messages.
- Publish your actual shipping and returns terms in `site.json` → `policies`. Review privacy wording for the hosting/payment/analytics services you actually use.
- Configure and test your payment provider, tax/shipping settings and stock limits.
- Set `siteUrl` to the canonical HTTPS site root. No made-up domain is included.
- Set `preview` to false; rebuild, check and deploy.
- Test on real mobile devices and desktop, including keyboard navigation and a provider test checkout.

## Replacing editorial images

Product images use their own `image` field. Homepage, category and About imagery can be replaced using `editorialImages` in `site.json`:

```json
"editorialImages": {
  "blue": "assets/hero-mineral.jpg",
  "purple": "assets/mineral-category.jpg",
  "pale": "assets/about-specimen.jpg",
  "green": "assets/gemstone-category.jpg",
  "pendant": "assets/jewelry-category.jpg"
}
```

Supply real files at those paths. The names are internal image slots, not asserted gemstone identities. Choose portraits for the hero and About sections. Replace the generic editorial alt descriptions in `pic()` in the builder with accurate descriptions of your final photographs.

## Branding

Recommended: **The Facet** — an elongated gem symbol, elegant serif wordmark and spaced COLLECTION line. It represents the whole business well.

Alternative: **The Collector** — a circular BM monogram with a luxury jewelry feel. Useful for a social avatar, packaging seal or box.

Both editable SVG concepts and a generated mood board are included. SVG wordmarks use live Georgia/Arial text: a designer can convert type to outlines for consistent professional printing. The concepts have not undergone trademark clearance.

## Verification performed

- Built all 23 pages successfully.
- Checked all generated local navigation/assets, page titles, descriptions, unique IDs, one main heading per page and valid JSON-LD.
- Checked both JavaScript files for syntax errors.
- Browser-tested product search, zero-results recovery, category filtering, alphabetical sorting and product inquiry prefill.
- Reviewed the desktop homepage and a 390px-wide layout; tested the narrow-screen navigation menu.
- Tested editor content loading, event-template creation and JSON validation.

The browser review is a focused functional check, not a formal accessibility audit. Payment, production-domain indexing and real-device testing require your final setup.

## References

- GitHub Pages usage limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Cloudflare Pages Git integration: https://developers.cloudflare.com/pages/configuration/git-integration/
- Cloudflare build configuration: https://developers.cloudflare.com/pages/configuration/build-configuration/
- Google AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- GIA colored stone reports: https://www.gia.edu/gem-education/colored-stone
- GIA gem treatments: https://www.gia.edu/gem-treatment
