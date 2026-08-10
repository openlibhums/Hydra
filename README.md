# Hydra Plugin for Janeway

Hydra is a **Janeway plugin** that enables

- the automatic **dispatch of submitted articles** from one journal to other journals within the same Janeway instance.

  This is particularly useful for publishers who publish translated versions of the same article in multiple journals. For example, the *International Labor Review (ILR)* uses Hydra to submit and review once, and then dispatch copies of the article to three language journals — avoiding duplicate submission and review workflows.

- the **linking of two articles** with a particular relationship

  This is useful to deal with errata, addenda, etc.

---

## Features

- Dispatch
  - Dispatch an article submitted to one journal to multiple other journals.
  - Maintain a single submission and review process. Child language articles are aware of each other and are interlinked.
  - Ideal for publishers managing language editions or derivative publications.
- Linking
  - Define the relationship between two articles
  - Display the relationship in the two articles' landing pages
  - Send the relationship to meta-engines such as crossref
  - Order the articles linked to the same "from article" (see `LinkedArticle.order`),
    which matters for sets such as commentaries, where an introductory paper gathers
    a number of invited contributions in a well-defined sequence


---

## Installation

1. **Clone the repository** into your Janeway `plugins` directory.
   ```bash
   cd path/to/janeway/src/plugins
   git clone https://github.com/openlibhums/Hydra/ hydra
   ```

2. **Install the plugin** from the Janeway directory:
   ```bash
   cd path/to/janeway
   python3 src/manage.py install_plugins hydra
   ```

   > If you're using Docker, use the equivalent Janeway Docker command.

3. **Run the required database migrations:**
   ```bash
   python3 src/manage.py migrate
   ```

4. **Restart your server** (Apache, Passenger, or your preferred server).

5. **Configure and enable the plugin** in the Janeway admin interface:
   Configuration of Hydra is handled via the Admin interface as it has no front end of its own.

---

## Usage Example

-Dispatch
  - An author submits an article to Journal A (Submission Journal).
  - Once accepted, **Hydra dispatches** copies to:
    - Journal B (English)
    - Journal C (French)
    - Journal D (Spanish)
  - Editors can then handle language versions without requiring separate submissions or reviews.
- Linking
  - An author submits an article A
  - After some time, the author submits another article B, that is an erratum of A
  - A new hydra "linked article" relationship is created in the admin between A and B
    - From article -> A
    - To article -> B
    - Relationship -> Erratum
  - Upon publication of B, crossref is informed of the relation between B and A



## License

Hydra is released under the AGPL v3 license as Janeway. See `LICENSE` for details.
