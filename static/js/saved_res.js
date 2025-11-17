document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("resources-grid");
    const loading = document.getElementById("loading");
    const empty = document.getElementById("empty-state");
    const stats = document.getElementById("total-count");
    const typeFilter = document.getElementById("type-filter");
    const clearFilterBtn = document.getElementById("clear-filter-btn");

    let allResources = [];
    let filteredResources = [];

    loadTypes();
    loadResources();

    // ============================
    //       LOAD TYPES
    // ============================
    async function loadTypes() {
        typeFilter.innerHTML = `<option value="">All types</option>`;

        const r = await fetch("/api/saved-resources/types");
        const data = await r.json();

        if (!data.types) return;

        data.types.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.id;
            opt.textContent = `${t.name} (${t.count})`;
            typeFilter.appendChild(opt);
        });
    }

    // ============================
    //     LOAD RESOURCES
    // ============================
    async function loadResources() {
        loading.style.display = "block";

        const r = await fetch("/api/saved-resources");
        const data = await r.json();

        loading.style.display = "none";

        allResources = data.resources || [];
        filteredResources = [...allResources];

        updateStats();
        renderResources();
    }

    // ============================
    //       UPDATE STATS
    // ============================
    function updateStats() {
        stats.textContent = filteredResources.length;
    }

    // ============================
    //        RENDER GRID
    // ============================
    function renderResources() {
        grid.innerHTML = "";

        if (filteredResources.length === 0) {
            empty.style.display = "block";
            return;
        }

        empty.style.display = "none";

        filteredResources.forEach(r => {
            const card = document.createElement("div");
            card.classList.add("resource-card");
            card.dataset.id = r.id;

            const helps = r.addressed_states?.length
                ? `
                <div class="resource-section">
                    <div class="resource-section-title">Helps with:</div>
                    <div class="tags-container">
                        ${r.addressed_states.map(s => `<span class="tag">${s}</span>`).join("")}
                    </div>
                </div>`
                : "";

            const themes = r.themes?.length
                ? `
                <div class="resource-section">
                    <div class="resource-section-title">Themes:</div>
                    <div class="tags-container">
                        ${r.themes.map(t => `<span class="tag">${t}</span>`).join("")}
                    </div>
                </div>`
                : "";

            card.innerHTML = `
                <div class="resource-header">
                    <div class="resource-title-section">
                        <h3>${r.title}</h3>
                        ${r.author ? `<p class="resource-author">by ${r.author}, ${r.language?.toUpperCase() || ""}</p>` : ""}
                    </div>
                    <div class="resource-type-badge">${r.resource_type || "Resource"}</div>
                </div>

                ${helps}
                ${themes}

                <p class="resource-description">
                    ${r.description ? r.description.substring(0, 200) : "No description"}
                </p>

                <div class="resource-actions">
                    <a href="${r.url}" class="btn btn-primary" target="_blank">
                        Open →
                    </a>
                    <button class="btn btn-secondary delete-btn" data-id="${r.id}">
                        Delete
                    </button>
                </div>
            `;

            grid.appendChild(card);
        });
    }

    // ============================
    //      FILTER CHANGE
    // ============================
    typeFilter.addEventListener("change", () => {
        const selected = typeFilter.value;

        if (!selected) {
            filteredResources = [...allResources];
        } else {
            filteredResources = allResources.filter(
                r => String(r.resource_type_id) === selected
            );
        }

        updateStats();
        renderResources();
    });

    // ============================
    //     CLEAR FILTER BUTTON
    // ============================
    clearFilterBtn.addEventListener("click", () => {
        typeFilter.value = "";
        filteredResources = [...allResources];
        updateStats();
        renderResources();
    });

    // ============================
    //   DELETE RESOURCE HANDLER
    // ============================
    document.addEventListener("click", async (e) => {
        if (e.target.classList.contains("delete-btn")) {
            const id = e.target.dataset.id;

            if (!confirm("Delete resource from saves?")) return;

            await deleteResource(id);
            await loadResources();
            await loadTypes();
        }
    });
});

// ============================
//    DELETE RESOURCE API
// ============================
async function deleteResource(id) {
    const res = await fetch(`/api/saved-resources/${id}`, {
        method: "DELETE"
    });

    const data = await res.json();

    if (!data.success) {
        alert("Error while deleting resource");
    }
}
