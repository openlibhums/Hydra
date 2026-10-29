# Hydra Plugin for Janeway

Hydra is a **Janeway plugin** that enables the automatic **dispatch of submitted articles** from one journal to other journals within the same Janeway instance.  

This is particularly useful for publishers who publish translated versions of the same article in multiple journals. For example, the *International Labor Review (ILR)* uses Hydra to submit and review once, and then dispatch copies of the article to three language journals — avoiding duplicate submission and review workflows.

---

## Features

- Dispatch an article submitted to one journal to multiple other journals.
- Maintain a single submission and review process. Child language articles are aware of each other and are interlinked.
- Ideal for publishers managing language editions or derivative publications.

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

- An author submits an article to Journal A (Submission Journal).
- Once accepted, **Hydra dispatches** copies to:
  - Journal B (English)
  - Journal C (French)
  - Journal D (Spanish)
- Editors can then handle language versions without requiring separate submissions or reviews.


## License

Hydra is released under the AGPL v3 license as Janeway. See `LICENSE` for details.
