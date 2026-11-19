# SATs website – review report (2026-11-19)

Scope: 21 live pages (index, 17 product pages, blog, blog-details, portfolio-details template) + 4 stray/backup pages, `assets/css/main.css`, `assets/js/main.js`.
Method: static audit of all HTML (comments stripped), broken-link/asset scan, tag-balance check, and real Chrome renders of index and one product page at 1440px and 390px.
**Nothing has been changed yet.**

## A. Not applied globally (fixed or written per page, never site-wide)

| # | Issue | Where |
|---|---|---|
| A1 | Same generic `<title>` and description on all 17 product pages; blog-details and portfolio-details still say "Impact Bootstrap Template" | 19 pages |
| A2 | og:/twitter: tags and canonical exist only on index.html (and og:image is empty even there) | 20 pages |
| A3 | Navigation differs: index = Home/About/Products/Contact; product pages = Home/About/Services/Portfolio/Contact; blog + portfolio-details = Team/Blog + demo "Drop Down" menu | every page |
| A4 | Nav "Contact" is `#contact` on 5 product pages that have no contact section, so the link does nothing | 5 pages |
| A5 | Top-bar social icons differ: index has Facebook/LinkedIn/YouTube; 20 other pages still show Twitter/Instagram | 20 pages |
| A6 | Top-bar email link is `mailto:contact@example.com` while the visible text is info.sats123@gmail.com | all 21 |
| A7 | Footer "Terms of service" goes nowhere; footer links to "Services"/"Portfolio" point at sections that are hidden or renamed on index | all 21 |
| A8 | Footer lists only 5 of the 17 products | all |
| A9 | No enquiry call-to-action on product pages (contact form exists only on index) | 17 pages |
| A10 | Every page is a copy-pasted shell, so each fix must be repeated 21 times | all |

## B. Real bugs

| # | Issue | Evidence |
|---|---|---|
| B1 | A stray `` ` `` is printed at the top-left of index (seen in the render) | index.html line 17, after `<!-- HTML Meta Tags -->` |
| B2 | A stray ``` ``` ``` breaks the services grid: the last cards are shifted/narrower and the final row is incomplete (seen in the render) | index.html ~line 477 |
| B3 | Contact section has unbalanced closing tags (13 structure errors on index) and inline `height:605px`; the info card renders narrower than its column | index.html |
| B4 | WhatsApp "Buy Now" links use `wa.me/7990042066` (no country code, should be `917990042066`) and unencoded message text | 3 pricing buttons |
| B5 | Scroll-to-top JS: `addEventListener('click', window.scrollTo(...))` runs scrollTo on page load and registers no click handler | main.js |
| B6 | 9 service cards link "Read more" to `#`; product pages exist for several of them | index.html |
| B7 | Missing images: `assets/img/portfolio/SATs-Probe-Station-*.jpg` (3 pages); `crayo_2.jpg`/`crayo_3.jpg` (real files are .jpeg/.png); `extranal_prob_crayo_2.png` (real file is .jpg) | 5 pages |
| B8 | Windows backslash paths (`sats_products\light_source\…`) work in Chrome but are fragile on other hosts/tools | index + 3 product pages |
| B9 | Curly quotes in attributes (`style=“text-align:justify”`) so the style is ignored (12 pages); `<p><h5>…</h5></h5>` and unclosed `<p>` give 16–22 structure errors per product page | 17 product pages |
| B10 | The "Project information" sidebar is commented out but the text column is still `col-lg-8`, so the right third of every product page is empty (seen in the render) | 17 pages |
| B11 | Swiper "not enough slides for loop" warning: single-image sliders are set to loop/autoplay | console, product pages |
| B12 | Pricing "Free Plan ₹0" has a "Buy Now" button | index |

## C. Alignment & formatting

- C1 Services grid: uneven card heights (AI-ML card is about twice as tall), four cards reuse the same icon, and the icon's grey circle sits off-centre behind the icon.
- C2 Product grid: image backgrounds vary (white / black / grey), images are not cropped to one ratio, and card heights are uneven.
- C3 Catalogue mismatch: Services lists Muffle Furnace, Potentiostat, Vibration-less Table and both Cryogenic stations, but the Products grid doesn't show them.
- C4 Empty "Team" section leaves a blank gap of about 120px between Products and Pricing.
- C5 Clients slider: logos are different sizes and aspect ratios (some tiny, one clipped at the edge).
- C6 Contact: info card and form are unequal widths; the Google Form iframe has a fixed 605px height and will clip on phones.
- C7 Footer: copyright block is centred while the columns are left-aligned; "Phone:(+91)" and "Email:" lack a space; wrapped links have tight line-height.
- C8 Heading hierarchy: `<h4><p>` in the hero; product pages jump h2→h3→h5.
- C9 Hero "Get brochure!" button is low-contrast against the green background.
- C10 Product page body is a flat text dump (small italic spec lines, no spec table, no CTA, no images beyond one).

## D. Animation

- D1 AOS is the only animation system; every element uses the same 1000ms with no stagger on grids, which feels slow.
- D2 Cards and buttons have minimal hover/press feedback.
- D3 No `prefers-reduced-motion` handling (autoplay sliders, pulse button, AOS).
- D4 Scroll handlers for header and active-nav are not throttled/passive.
- D5 Preloader is removed only on window `load`, so it waits on every heavy image.

## E. Content / copy (needs your confirmation)

- E1 Typos: "approches", "We offers variety of the products...", "10AM - 18PM".
- E2 Product pages still reuse the template's quote block ("Simple living and high thinking.").
- E3 17 empty `alt=""` on index (client logos and product images) and 1–4 on every product page.
- E4 Phone, email and address are hand-typed in 4 places per page.

## F. SEO / performance / accessibility

- F1 Index head has duplicate `<title>` and `description`, and Facebook/Twitter meta sits before `<meta charset>`.
- F2 Both gtag.js and Google Tag Manager are loaded on index.
- F3 Repo is 50 MB, no `loading="lazy"`, no `width/height` on images (layout shift).
- F4 `bootstrap-icons.css` (98 KB, unminified) is loaded; Poppins is referenced in CSS but never loaded.
- F5 No `sitemap.xml`, `robots.txt`, 404 page, skip link or `:focus-visible` styles.
- F6 The GitHub Pages workflow publishes the whole repo, including backup pages.

## G. Clutter (decision needed)

`updated_index.html`, `updated indexx_1.html`, `index__UNDER_MAINTENCANCE.html`, `sample-inner-page.html`, `portfolio-details.html`, `blog.html`, `blog-details.html` (template demos). `portfolio-details-Probesstation.html` and `portfolio-details-low-temp-probe-station.html` are both "Micro-Probe Station" pages. File names with spaces/capitals: `portfolio-details-SATS Potentiostat.html`.
