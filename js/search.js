
let fuse;
let allKeywords = [];
// NEW: Map to store LibraryName -> Base URL
let libraryUrls = {}; 

const resultsDiv = document.getElementById("results");
const searchBox = document.getElementById("searchBox");
const modal = document.getElementById("keywordModal");
const closeModal = document.getElementById("closeModal");

function getFirstParagraph(html) {
    if (!html) return "No documentation available.";
    
    const matchP = html.match(/<p>(.*?)<\/p>/i);
    if (matchP && matchP[1]) {
        return matchP[1];
    }
    
    const summary = html.split(/\n\s*\n/)[0].trim();
    
    return summary || "No documentation available.";
}

function initializeLibraryLinks() {
    const navLinks = document.querySelectorAll('.nav-links a');
    
    // Loop through all navigation links
    navLinks.forEach(link => {
        // Only process links that point to library.html (i.e., the library links)
        if (link.href.includes("library.html?lib=")) {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Stop the browser from navigating to library.html

                // Extract the library name from the query string
                const urlParams = new URLSearchParams(new URL(this.href).search);
                const libName = urlParams.get('lib');
                
                // Look up the base URL from the map
                const baseUrl = libraryUrls[libName];

                if (baseUrl) {
                    window.open(baseUrl, '_blank');
                } else {
                    console.error('Base URL not found for library:', libName);
                }
            });
        }
    });
}

fetch('./data/keywords.json')
    .then(response => response.json())
    .then(keywords => {
        allKeywords = keywords;
        
        // 1. Build the unique libraryUrls map 
        // We use the full URL from the first keyword entry for each library.
        keywords.forEach(kw => {
            if (!libraryUrls[kw.library] && kw.url) {
                // Extract the base URL by stripping the anchor (which starts with '#')
                const baseUrl = kw.url.split('#')[0];
                libraryUrls[kw.library] = baseUrl;
            }
        });

        // 2. Initialize search functionality
        fuse = new Fuse(allKeywords, {
            keys: [
                { name: "name", weight: 0.8 },
                { name: "library", weight: 0.1 },
                { name: "doc", weight: 0.1 }
            ],
            threshold: 0.3, 
            distance: 50,  
            location: 0,
            tokenize: true,
            matchAllTokens: true,   
            useExtendedSearch: true, 
            ignoreFieldNorm: true,
            includeScore: true
        });

        // 3. Attach event listeners to navigation bar
        initializeLibraryLinks();
    });

function runSearch(query) {
    // ... (runSearch function logic remains unchanged) ...
    const trimmed = query.trim();
    resultsDiv.innerHTML = "";
    if (trimmed.length === 0) {
        resultsDiv.style.display = "none";
        return;
    }
    if (!fuse) return;

    const allResults = fuse.search(trimmed).map(r => r.item);

    const groupedKeywords = allResults.reduce((acc, keyword) => {
        if (!acc[keyword.name]) {
            acc[keyword.name] = [];
        }
        acc[keyword.name].push(keyword);
        return acc;
    }, {});
    
    const resultsToDisplay = Object.values(groupedKeywords);

    resultsDiv.style.display = "grid";
    
    resultsToDisplay.forEach(group => {
        const keywordName = group[0].name;
        const libraries = group.map(k => k.library).join(", "); 
        
        const div = document.createElement("div");
        div.classList.add("result-card", "fade-in");
        
        div.innerHTML = `
            <div class="result-title">${keywordName}</div>
            <div class="result-lib">${libraries}</div>
        `;
        
        div.onclick = () => openModal(group); 
        resultsDiv.appendChild(div);
    });
}

searchBox.addEventListener("input", e => runSearch(e.target.value));

function openModal(keywordOrKeywords) {
    // ... (openModal function logic remains unchanged) ...
    let keyword;
    let availableKeywords = [];

    if (Array.isArray(keywordOrKeywords)) {
        keyword = keywordOrKeywords[0];
        availableKeywords = keywordOrKeywords;
    } else {
        keyword = keywordOrKeywords;
        availableKeywords = [keywordOrKeywords];
    }
    
    const modalTitle = document.getElementById("modalTitle");
    const modalLibrary = document.getElementById("modalLibrary");
    const modalArgs = document.getElementById("modalArgs");
    const modalDoc = document.getElementById("modalDoc");
    const openDocsBtn = document.getElementById("openDocs");
    const copyBtn = document.getElementById("copyKeyword");
    const toast = document.getElementById("toast");
    
    modalTitle.innerText = keyword.name;

    if (availableKeywords.length > 1) {
        const libraryList = availableKeywords.map(k => k.library).join(', ');
        modalLibrary.innerText = 'Libraries: ' + libraryList;
    } else {
        modalLibrary.innerText = "Library: " + keyword.library;
    }
    
    // FIX: Ensure we use requiredArgs and handle the case of no required arguments
    modalArgs.innerText = (keyword.requiredArgs && keyword.requiredArgs.length > 0) 
                        ? keyword.requiredArgs.join(", ") 
                        : "None";
    
    modalDoc.innerHTML = getFirstParagraph(keyword.doc);

    openDocsBtn.onclick = () => window.open(keyword.url, "_blank");

    copyBtn.onclick = () => {
        navigator.clipboard.writeText(keyword.name);
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 1000);
    };

    modal.style.display = "flex";
}

closeModal.onclick = () => (modal.style.display = "none");
window.onclick = e => {
    if (e.target === modal) modal.style.display = "none";
}
