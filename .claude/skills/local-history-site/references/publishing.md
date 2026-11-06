# Permission and publishing

## Before permission

- Preview locally.
- If the code lives on GitHub, keep the repository private, or keep the image files out
  of it, until the archive says yes. Anything in a public repo can be copied and cached
  even after you delete it.
- GitHub Pages from a private repository needs a paid plan, so a private repo usually
  means local previews only.

## The permission email

Draft it for the person to send from their own address. Fill in the specifics, and keep
it short.

```
Subject: Permission to use photos from your collection on a [Town] history website

Hello [name or "there"],

I'm [name], [connection: grew up in Town / a member / a descendant of …]. I'm building
a free, non-commercial website that tells [Town]'s history in [N] short chapters, each
with one photo from your collection. [Preview link, or the list of images with your
catalog numbers.]

- Each image is credited to [Archive], with its date where known, and the site links
  to your website [and museum].
- The photos are shown with an ink-tone filter (contrast, color and grain only).
  Nothing in them is added or changed. [I removed handwritten captions from two prints.]
- The site isn't affiliated with [Archive], and I'll take down anything you'd rather
  I didn't use.

May I have your permission to use these images? If you have higher-resolution scans of
any of them, I'd be glad to use those instead. I'd also welcome a fact-check of the
text.

Thank you,
[name]
[email / phone]
```

Record the answer and any conditions, such as a specific credit wording or a link back,
in `sources.md` or the README.

## GitHub Pages

- Settings → Pages → Deploy from a branch → `main`, folder `/`. Add an empty `.nojekyll`
  file so files are served exactly as they are.
- The site appears at `https://<user>.github.io/<repo>/`.

## A custom domain

**A subdomain is the simplest choice,** for example `history.example.com`.
1. At the DNS host, add a CNAME record:
   - Host: `history`. Most DNS hosts add the domain themselves, so enter only the host
     part.
   - Value: `<user>.github.io.`
2. In the repo, go to Settings → Pages → Custom domain, enter `history.example.com` and
   save.
   - GitHub commits a `CNAME` file to the publishing branch.
   - Pull it before pushing other work, or the next push will conflict.
3. Wait for the HTTPS certificate, usually within an hour, then tick **Enforce HTTPS**.
   If it seems stuck, remove the custom domain and add it again.

The old `github.io` address redirects to the new one automatically.

**A path on an existing domain,** such as `www.example.com/town-history/`: this only
works when that domain is set on the account's user site, the repo named exactly
`<user>.github.io`.
- Every project repo with Pages turned on and no domain of its own then appears under
  that domain at `/<repo>/`.
- If the domain belongs to some other project repo instead, other repos won't appear
  under it, and the path returns 404.
- Check which repo holds the domain before promising a URL:
  `gh api repos/<user>/<repo>/pages --jq .cname`.

**Apex domain** (`example.com`):
- A records: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
- AAAA records: 2606:50c0:8000::153 through 2606:50c0:8003::153.
- Point `www` at `<user>.github.io.` with a CNAME.

## Verify the domain (recommended)

Verification stops anyone else from attaching a subdomain of it to their own GitHub Pages
site.
1. Go to GitHub → profile picture → Settings → Pages, the account's settings rather than
   the repo's. Click **Add a domain** and enter the bare domain (`example.com`).
2. GitHub shows a TXT record named `_github-pages-challenge-<user>` with a code. Add it at
   the DNS host, entering only that host part.
3. Check that it's live: `dig +short TXT _github-pages-challenge-<user>.example.com`
   should print the code. This takes minutes, or occasionally up to a day.
4. Click **Verify**. Keep the TXT record in place afterwards; the domain stays verified
   only while it exists.

Verification covers the domain's immediate subdomains. Avoid wildcard DNS records
(`*.example.com`): they leave deeper names open to takeover even when the domain is
verified.

## Other hosts

Any static host works the same way: Netlify, Cloudflare Pages, a university web space or
the historical society's own server. The site is just files.

## After launch

- Send the archive the live link and thank them.
- Put a way to send corrections in the colophon. Local readers will find things, and
  `sources.md` makes fixing them quick.
