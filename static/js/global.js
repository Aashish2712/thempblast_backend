/* ============================================================
   THE MP BLAST — Global JavaScript
   ------------------------------------------------------------
   Responsibilities:
   - Load shared homepage/global data
   - Render breaking ticker site-wide
   - Render dynamic categories in:
       1. Desktop navbar
       2. Mobile offcanvas menu
       3. Footer
   - Keep Django/API as the source of truth
   ============================================================ */

(function () {
    "use strict";

    /* ============================================================
       GLOBAL STATE
       ============================================================ */

    window.HOME_DATA = window.HOME_DATA || {
        breaking: [],
        hero: [],
        latest: [],
        categories: []
    };

    window.MPB_GLOBAL = window.MPB_GLOBAL || {
        categories: []
    };


    /* ============================================================
       TEMPORARY V1 COMPATIBILITY CATEGORIES
       ------------------------------------------------------------
       These are used only if /api/home/ does not return categories.

       Once the backend reliably returns categories from
       /api/home/, this fallback can be removed.
       ============================================================ */

    const DEFAULT_CATEGORIES = [
        {
            name: "राजनीति",
            slug: "politics",
            is_active: true,
            displayOrder: 1
        },
        {
            name: "अपराध",
            slug: "crime",
            is_active: true,
            displayOrder: 2
        },
        {
            name: "शिक्षा",
            slug: "education",
            is_active: true,
            displayOrder: 3
        },
        {
            name: "व्यापार",
            slug: "business",
            is_active: true,
            displayOrder: 4
        },
        {
            name: "खेल",
            slug: "sports",
            is_active: true,
            displayOrder: 5
        },
        {
            name: "मनोरंजन",
            slug: "entertainment",
            is_active: true,
            displayOrder: 6
        },
        {
            name: "राष्ट्रीय",
            slug: "national",
            is_active: true,
            displayOrder: 7
        },
        {
            name: "मध्य प्रदेश",
            slug: "mp",
            is_active: true,
            displayOrder: 8
        }
    ];


    /* ============================================================
       UTILITY — HTML ESCAPE
       ============================================================ */

    function escapeHtml(value) {
        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    /* ============================================================
       UTILITY — NORMALIZE CATEGORY
       ============================================================ */

    function normalizeCategory(category, index) {
        if (!category) {
            return null;
        }

        /*
         * Backend may return:
         *
         * {
         *     category: {...},
         *     articles: [...]
         * }
         *
         * OR directly:
         *
         * {
         *     name: "...",
         *     slug: "..."
         * }
         */

        let item = category.category || category;

        if (!item || typeof item !== "object") {
            return null;
        }

        const name =
            item.name ||
            item.title ||
            item.category_name ||
            "";

        const slug =
            item.slug ||
            item.category_slug ||
            "";

        if (!name || !slug) {
            return null;
        }

        const isActive =
            item.is_active !== undefined
                ? item.is_active
                : (
                    item.isActive !== undefined
                        ? item.isActive
                        : true
                );

        const displayOrder =
            Number(
                item.displayOrder ??
                item.display_order ??
                item.order ??
                index + 1
            );

        let url = item.url || item.href || "";

        if (!url) {
            url = `/category/${encodeURIComponent(slug)}/`;
        }

        return {
            name: String(name),
            slug: String(slug),
            is_active: Boolean(isActive),
            displayOrder: Number.isFinite(displayOrder)
                ? displayOrder
                : index + 1,
            url: String(url)
        };
    }


    /* ============================================================
       NORMALIZE + SORT + DEDUPLICATE CATEGORIES
       ============================================================ */

    function normalizeCategories(categories) {
        if (!Array.isArray(categories)) {
            return [];
        }

        const normalized = categories
            .map(normalizeCategory)
            .filter(Boolean)
            .filter(category => category.is_active);

        const unique = [];
        const seen = new Set();

        normalized.forEach(category => {
            const key = category.slug.toLowerCase();

            if (seen.has(key)) {
                return;
            }

            seen.add(key);
            unique.push(category);
        });

        unique.sort(function (a, b) {
            return a.displayOrder - b.displayOrder;
        });

        return unique;
    }


    /* ============================================================
       GET CATEGORY DATA
       ============================================================ */

    function getCategories() {
        return Array.isArray(window.MPB_GLOBAL.categories)
            ? window.MPB_GLOBAL.categories
            : [];
    }


    /* ============================================================
       CATEGORY URL
       ============================================================ */

    function getCategoryUrl(category) {
        if (
            category &&
            category.url &&
            typeof category.url === "string"
        ) {
            return category.url;
        }

        if (category && category.slug) {
            return `/category/${encodeURIComponent(category.slug)}/`;
        }

        return "#";
    }


    /* ============================================================
       DESKTOP NAVIGATION
       ============================================================ */

    function renderDesktopNavigation() {
        const nav = document.getElementById("desktopCategoryNav");

        if (!nav) {
            return;
        }

        /*
         * Keep fixed utility links.
         */

        nav.innerHTML = "";

        const homeLink = document.createElement("a");

        homeLink.href = "/";
        homeLink.setAttribute("data-nav-home", "");
        homeLink.textContent = "होम";

        nav.appendChild(homeLink);


        const latestLink = document.createElement("a");

        latestLink.href = "/#latest";
        latestLink.setAttribute("data-nav-latest", "");
        latestLink.textContent = "ताज़ा खबरें";

        nav.appendChild(latestLink);


        /*
         * Dynamic categories
         */

        const categories = getCategories();

        categories.forEach(function (category) {
            const link = document.createElement("a");

            link.href = getCategoryUrl(category);
            link.textContent = category.name;

            link.setAttribute("data-category-slug", category.slug);

            nav.appendChild(link);
        });
    }


    /* ============================================================
       MOBILE NAVIGATION
       ============================================================ */

    function renderMobileNavigation() {
        const nav = document.getElementById("mobileCategoryNav");

        if (!nav) {
            return;
        }

        nav.innerHTML = "";


        //Home

        const homeLink = document.createElement("a");

        homeLink.href = "/";
        homeLink.className = "nav-link";
      
        homeLink.setAttribute("data-nav-home", "");

        homeLink.innerHTML = `
             होम
            <i class="bi bi-house-door me-2"></i>
        `;

        nav.appendChild(homeLink);


        
          //Latest News
         

        const latestLink = document.createElement("a");

        latestLink.href = "/#latest";
        latestLink.className = "nav-link";
   
        latestLink.setAttribute("data-nav-latest", "");

        latestLink.innerHTML = `
             ताज़ा खबरें
            <i class="bi bi-lightning-charge me-2"></i>
        `;

        nav.appendChild(latestLink);


         //Dynamic categories
         

        const categories = getCategories();

        categories.forEach(function (category) {
            const link = document.createElement("a");

            link.href = getCategoryUrl(category);
            link.className = "nav-link";

      
            link.setAttribute("data-category-slug", category.slug);

            link.innerHTML = `
                ${escapeHtml(category.name)}
                <i class="bi bi-chevron-right me-2"></i>
            `;

            nav.appendChild(link);
        });
    }
document.addEventListener("click", function (event) {
    const link = event.target.closest("#mobileCategoryNav a");

    if (!link) {
        return;
    }

    const offcanvasElement = document.getElementById("mobileNav");

    if (!offcanvasElement) {
        return;
    }

    const offcanvas = bootstrap.Offcanvas.getInstance(offcanvasElement);

    if (offcanvas) {
        offcanvas.hide();
    }

    // IMPORTANT:
    // Do NOT use event.preventDefault()
    // The browser must continue with the link navigation.
});

    /* ============================================================
       FOOTER CATEGORY NAVIGATION
       ============================================================ */

    function renderFooterNavigation() {
        const nav = document.getElementById("footerCategoryNav");

        if (!nav) {
            return;
        }

        nav.innerHTML = "";

        const categories = getCategories();

        categories.forEach(function (category) {
            const li = document.createElement("li");

            const link = document.createElement("a");

            link.href = getCategoryUrl(category);
            link.textContent = category.name;

            link.setAttribute("data-category-slug", category.slug);

            li.appendChild(link);
            nav.appendChild(li);
        });
    }


    /* ============================================================
       RENDER ALL NAVIGATION
       ============================================================ */

    function renderNavigation() {
        renderDesktopNavigation();
        renderMobileNavigation();
        renderFooterNavigation();
    }


    /* ============================================================
       BREAKING TICKER
       ------------------------------------------------------------
       IMPORTANT:
       No frontend fallback is used here.

       Backend /api/home/ decides what appears in breaking.
       ============================================================ */
function renderTicker() {
    const tickerTrack = document.getElementById("tickerTrack");

    if (!tickerTrack) {
        console.warn("THE MP BLAST: #tickerTrack not found.");
        return;
    }

    const breaking = Array.isArray(window.HOME_DATA.breaking)
        ? window.HOME_DATA.breaking
        : [];

    /*
     * Backend is the source of truth.
     * Do not create frontend article fallback.
     */

    tickerTrack.innerHTML = "";

    if (breaking.length === 0) {
        const emptyItem = document.createElement("span");

        emptyItem.className = "ticker-item";
        emptyItem.textContent =
            "अभी कोई ब्रेकिंग न्यूज़ उपलब्ध नहीं है।";

        tickerTrack.appendChild(emptyItem);

        return;
    }

    breaking.forEach(function (article) {
        if (!article) {
            return;
        }

        const title =
            article.title ||
            article.headline ||
            article.name ||
            "ब्रेकिंग न्यूज़";

        const slug =
            article.slug ||
            article.articleSlug ||
            "";

        const item = document.createElement("span");

        item.className = "ticker-item";

        if (slug) {
            const link = document.createElement("a");

            link.href =
                `/article/${encodeURIComponent(slug)}/`;

            link.textContent = title;

            item.appendChild(link);
        } else {
            item.textContent = title;
        }

        tickerTrack.appendChild(item);
    });
}

    /* ============================================================
       LOAD GLOBAL DATA
       ------------------------------------------------------------
       /api/home/ is currently the shared source for:
       - breaking
       - hero
       - latest
       - categories
       ============================================================ */

    async function loadGlobalData() {
        try {
            const response = await fetch("/api/home/", {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (!response.ok) {
                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const data = await response.json();


            /* ----------------------------------------------------
               Update global data
               ---------------------------------------------------- */

            window.HOME_DATA = {
                breaking: Array.isArray(data.breaking)
                    ? data.breaking
                    : [],

                hero: Array.isArray(data.hero)
                    ? data.hero
                    : [],

                latest: Array.isArray(data.latest)
                    ? data.latest
                    : [],

                categories: Array.isArray(data.categories)
                    ? data.categories
                    : []
            };


            /* ----------------------------------------------------
               Categories
               ---------------------------------------------------- */

            let categories =
                normalizeCategories(data.categories);


            /*
             * V1 compatibility:
             *
             * If backend doesn't yet return category objects,
             * use the known V1 categories.
             *
             * This does NOT create article fallback data.
             * It only keeps navigation visible.
             */

            if (categories.length === 0) {
                categories =
                    normalizeCategories(DEFAULT_CATEGORIES);
            }


            window.MPB_GLOBAL.categories = categories;


            /* ----------------------------------------------------
               Render shared UI
               ---------------------------------------------------- */

            renderNavigation();
            renderTicker();


            /*
             * Dispatch an event so homepage/category pages can
             * react after global data has loaded.
             */

            document.dispatchEvent(
                new CustomEvent("mpb:global-data-loaded", {
                    detail: {
                        data: window.HOME_DATA,
                        categories: categories
                    }
                })
            );


            return data;

        } catch (error) {

            console.error(
                "THE MP BLAST: Failed to load global data:",
                error
            );


            /*
             * Keep navigation functional even if API fails.
             */

            const categories =
                normalizeCategories(DEFAULT_CATEGORIES);

            window.MPB_GLOBAL.categories = categories;

            renderNavigation();

            /*
             * Do not create breaking/hero/latest article
             * fallback content.
             */

            window.HOME_DATA.breaking = [];
            window.HOME_DATA.hero = [];
            window.HOME_DATA.latest = [];

            renderTicker();


            document.dispatchEvent(
                new CustomEvent("mpb:global-data-error", {
                    detail: {
                        error: error
                    }
                })
            );
        }
    }


    /* ============================================================
       LOAD CATEGORIES
       ------------------------------------------------------------
       Public helper.
       ============================================================ */

    async function loadCategories() {
        await loadGlobalData();

        return getCategories();
    }


    /* ============================================================
       PUBLIC API
       ============================================================ */

    window.renderTicker = renderTicker;

    window.loadGlobalData = loadGlobalData;

    window.renderNavigation = renderNavigation;

    window.loadCategories = loadCategories;


    /* ============================================================
       INITIALIZATION
       ============================================================ */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            /*
             * Render compatibility navigation immediately.
             * This prevents the navbar/footer from appearing empty
             * while the API request is running.
             */

            window.MPB_GLOBAL.categories =
                normalizeCategories(DEFAULT_CATEGORIES);

            renderNavigation();


            /*
             * Load the authoritative backend data.
             */

            loadGlobalData();
        }
    );

})();