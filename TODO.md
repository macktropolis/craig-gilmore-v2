# To Do

Open work for the Craig Gilmore site. See [CURRENT-STATE.md](CURRENT-STATE.md) for how the project fits together.

## Launch

- [ ] **Confirm the Cloudflare setup.** Check the `craig-gilmore-v2` Worker's production branch is `main` and that the latest deploy succeeded.
- [ ] **Point the domain at Cloudflare.** Move www.craiggilmore.net from WordPress to the Worker. Spot-check a few old WordPress URLs afterwards to confirm the redirects in `public/_redirects` work.

## Content from Craig

- [ ] **Brevo signup form.** Craig already has a Brevo account.
  - Create a form with double opt-in and EMAIL and FIRSTNAME fields.
  - Set its confirmation to redirect to `https://www.craiggilmore.net/ethereal/thanks/`.
  - Paste its `sibforms.com/serve/…` form URL into `BREVO_FORM_URL` in `src/data/site.ts`. Until then the Ethereal page shows a mailto button.
  - Once it's live, test one real signup: it should land on the thank-you page and the contact should appear in Brevo.
- [ ] **Sharper Thor image.** The first hero slide (`public/images/home/hero-thor.webp`) is only 658 px wide and looks soft on wide screens. Swap in a larger file if Craig has one, or start the slideshow on a sharper piece.
- [ ] **Studio photo of Craig.** The homepage and About photo (`public/images/home/craig-portrait.webp`) is a casual selfie shown in black and white. A photo of Craig at work would look more professional.

## Old WordPress site (security)

Make no changes to the live site without asking.

- [ ] Check wp-admin for hidden admin accounts. The REST API only lists users who have published posts.
- [ ] Run a Wordfence scan for backdoors.
- [ ] Check Google Search Console for spam pages that are still indexed and for security warnings.

## Done

- [x] Rebuild the site in Astro from the WordPress content: 68 projects, 7 news posts and the uploads.
- [x] Add a favicon, touch icons and a web manifest from Craig's logo.
- [x] Add a mobile menu, a 404 page, the Cloudflare `wrangler.jsonc`, and redirects from the old URLs.
- [x] Polish the design: Anton headings, hero slideshow, floating header, larger logo, artwork banners, thumbnails, lightbox and accessibility.
- [x] Restore 12 storyboard images that were lost to file-name case clashes.
