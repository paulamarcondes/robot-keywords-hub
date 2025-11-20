# Robot Framework Keyword Hub

A clean, fast, and searchable hub for all keywords across various popular Robot Framework libraries. 
Built to provide quick, concise access to keyword documentation, arguments, and official documentation links.


## Live Demo

You can access the live, deployed version of the application here:

> **[Robot Keyword Hub - Live Demo](https://paulamarcondes.github.io/robot-keywords-hub/)**


--

## Key Features

* **Concise Documentation:** Keyword documentation in the modal is strictly limited to the **first paragraph/summary**, ensuring users get the essential information quickly.
* **Cross-Library Grouping:** Keywords available in multiple libraries (e.g., `Get Title`) are consolidated into a single search result card, clearly listing all available libraries.
* **Instant Modal View:** Provides one-click access to the keyword's name, library, required arguments, and a link to the official documentation.


--

## Technology Stack

The Keyword Hub is a purely client-side application built with:

* **HTML5 / CSS3**
* **JavaScript (ES6+)**
* **Fuse.js (v6.6.2):** High-performance fuzzy-search library.
* **Data Source:** Keywords are sourced from local `.json` files.


--

## Local Setup

To run this project on your local machine, follow these simple steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/paulamarcondes/robot-keywords-hub.git
    cd robot-keywords-hub
    ```

2.  **Run Locally (Requires Python):** Use Python's built-in simple HTTP server to serve the static files:
    ```bash
    # Run from the project root directory
    python -m http.server 8000
    ```

3.  **View the Hub:** Open your web browser and navigate to `http://localhost:8000`.


--

## Contributing: Adding a New Library

To add a new Robot Framework library to the Keyword Hub, follow the steps.

### Steps:

1.  **Install the Library Locally**
    Use `pip` to install the library and the necessary prerequisites into your Python environment:

    ```bash
    pip install robotframework <library-name>
    ```

2.  **Generate the Libdoc JSON File**
    Use the `libdoc` tool (built into Robot Framework) to generate the official keyword documentation into a JSON file inside the `data/` folder.

    ```bash
    python -m robot.libdoc <LibraryName> data/<LibraryName>.json
    ```

    *Example for the Appium Library:*

    ```bash
    python -m robot.libdoc AppiumLibrary data/AppiumLibrary.json
    ```


3.  **Process and Integrate New Keywords**
    Run the build script located in the `py/` folder. 
    This script reads all individual JSON files in the `data/` folder, processes them, and compiles a clean, aggregated set of keywords into the single production file, `keywords.json`.

    ```bash
    python py/build_keywords.py
    ```


4.  **Add Keyword Documentation URL**
    Add the Keyword Documentation URL in your `build_keywords.py` file, on the `LIB_DOC_BASE` section.


5.  **Add Library to Navigation Bar**
    Add the new Library to the `index.html` file, under the `class="nav-links"` section.


--
## Conclusion

I hope this tool speeds up your test automation development process by providing fast, reliable keyword information. We welcome contributions and feedback to help improve the hub!
