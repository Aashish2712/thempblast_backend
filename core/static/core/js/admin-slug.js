(function () {
    "use strict";

    function setupSlug(sourceId, slugId) {
        const source = document.getElementById(sourceId);
        const slug = document.getElementById(slugId);

        if (!source || !slug) {
            return;
        }

        let slugManuallyEdited = slug.value.trim() !== "";

        slug.addEventListener("input", function () {
            slugManuallyEdited = true;
        });

        source.addEventListener("input", async function () {
            if (slugManuallyEdited) {
                return;
            }

            const value = source.value.trim();

            if (!value) {
                slug.value = "";
                return;
            }

            try {
                const response = await fetch(
                    `/admin/slugify/?text=${encodeURIComponent(value)}`,
                    {
                        credentials: "same-origin",
                        headers: {
                            "X-Requested-With": "XMLHttpRequest",
                        },
                    }
                );

                if (!response.ok) {
                    return;
                }

                const data = await response.json();

                if (data.slug) {
                    slug.value = data.slug;
                }
            } catch (error) {
                console.error("Slug generation failed:", error);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        setupSlug("id_name", "id_slug");
        setupSlug("id_headline", "id_slug");
    });
})();
