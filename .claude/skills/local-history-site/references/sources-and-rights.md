# Sources and rights

## Where to find images

Start local and work outward. Local collections have the photos nobody else has, and
the people who know what's in them.

- **The local historical society or museum.**
  - Look at its website galleries, newsletters (often full of captioned photos) and
    Facebook page.
  - Many have far more than they've put online, so ask.
- **The public library:** its local history room and digital collections.
- **The county historical society** and the county library.
- **State collections:**
  - the state's digital "memory" project, if it has one (for example, Ohio Memory);
  - the state historical society;
  - the state archives.
- **University special collections,** especially for company towns, industries and
  regional newspapers.
- **National collections:**
  - the Library of Congress (loc.gov). Many items are marked "no known restrictions", and
    it holds Sanborn fire insurance maps of many towns.
  - the Digital Public Library of America (dp.la), which searches many collections at
    once;
  - Wikimedia Commons and Flickr Commons. Check each file's license.
  - Outside the US: the national library, Europeana, Trove and similar.
- **Newspapers:** Chronicling America (loc.gov), state newspaper archives, and the local
  paper's own morgue.
- **Postcards, plat maps, atlases and aerial photos.** These are good for chapters that
  have no photograph.

## Where to find facts

- **Anniversary or centennial books,** often reprinted or put online by the historical
  society. They're rich in detail but boosterish.
- **Nineteenth-century county histories** ("History of X County"). These are often
  public domain on the Internet Archive or Google Books. They're useful for names and
  dates and unreliable for anything flattering.
- **Historical society articles and newsletters.**
- **National Register of Historic Places nomination forms.** They're detailed and usually
  footnoted, so they're a good check on building dates.
- **Newspapers from the time,** which are the best source for a specific event's date.
- **Company and church histories.**
- **Wikipedia,** only as a cross-check and a pointer to the sources it cites. Don't treat
  it as a source on its own.

## Searching a big gallery

Some galleries have thousands of captioned photos across many pages. To find candidates
for each chapter:
- collect the captions and image URLs into a local JSON file and search it by keyword
  (place names, businesses, years, events);
- do it politely: one request at a time, a plain descriptive User-Agent (no personal
  email), and cache what you've fetched so you never fetch it twice;
- respect robots.txt and the site's terms;
- keep the catalog out of the repo.

**Get exact image URLs from the gallery's HTML.** Filenames such as "scenes 2017 35" vs
"scenes 2017 035" are easy to guess wrong.

## The ledger: `production/sources.md`

Write it as you research, not afterwards. A good shape:

```markdown
# Sources

## Main sources
- **CHR**: "100-Year Chronology", from the 1933 Centennial Book. <url>
- **SET**: "The Settlement of …", <author>. <url>
- **WIKI**: <url>   (cross-check only)

## Facts by chapter

### 3. The Canal Comes Through
- The canal reached town in 1845; it ran about 250 miles. (CAN)
- Boats were 70–80 ft long, pulled by mules. (CAN)
- Image: <archive id>, "<archive's caption>". Taken after 1904, so the credit says so.

## Left out on purpose
- 1913 flood: dropped to keep the story upbeat (the person's choice).
- Land purchase size: SET says 10 acres, CAN says 80. Not used.

## To verify before publishing
- Museum addresses.
```

**Record these explicitly:**
- **Conflicts.** For example, sources that give 1931 vs 1932, or 1974 vs 1975.
  - Prefer the primary or contemporary source.
  - If it's still unresolved, write around it ("the mid-1970s", "the late 1950s").
  - Note both versions.
- **General context.** Statements from general knowledge rather than a cited source, such
  as "in the middle of the Depression". Mark them as such so a fact-checker knows.
- **Paraphrases of a quote.** Put the original wording beside the copy's wording, so
  anyone can check the paraphrase is fair.
- **Image identifications you made yourself.** For example, "the round building is the
  pavilion: its roof and posts match the photo in <article>".

## Rights, briefly (not legal advice)

- **Copyright and the physical print are separate things.** A society can own a print
  whose copyright expired long ago, or one whose copyright belongs to a photographer's
  family.
- **US public domain.**
  - Works *published* in the US before 1931 are public domain as of 2026. The line moves
    forward a year every January 1.
  - Unpublished photos, which describes many in local collections, follow different and
    longer rules.
  - Many local photos have no clear status.
- **Terms of use.** Even for public-domain images, an archive may set terms for its scans.
- **Ask anyway.** For a local project this is the decisive point: it's courteous, it
  builds the relationship, and it often gets you better scans and a fact-checker.
- **Text.** Facts aren't copyrightable, but prose is. Write the copy in your own words,
  keep any quotes short and credited, and credit the histories you drew on in the
  colophon.
