/*
 * TravelBuddySA Recommendations
 * API assumptions are centralised here so the team can align them with the actual DRF routes.
 *
 * Preferred endpoint:
 *   GET /api/recommendations/
 * Optional fallback endpoints:
 *   GET /api/destinations/
 *   GET /api/events/
 *
 * If the recommendation endpoint is unfinished, the page attempts the two listing endpoints
 * and applies a simple interest match in the browser. This is rule-based, not ML.
 */
(() => {
  "use strict";

  const CONFIG = {
    apiBase: "", // Example: "http://127.0.0.1:8000" if frontend and backend use different origins.
    recommendationsPath: "/api/recommendations/",
    destinationsPath: "/api/destinations/",
    eventsPath: "/api/events/",
    // Change these to the real detail-page filenames used by the team.
    destinationDetailPath: "destination-details.html",
    eventDetailPath: "event-details.html",
    requestTimeoutMs: 12000,
    // Set this to the token key used by your login code, if authentication is token-based.
    tokenStorageKeys: ["access", "access_token", "token"]
  };

  const state = {
    items: [],
    filteredItems: [],
    userInterests: [],
    activeQuickFilter: "all",
    loading: false
  };

  const els = {
    grid: document.getElementById("recommendation-grid"),
    status: document.getElementById("status-region"),
    empty: document.getElementById("empty-state"),
    emptyTitle: document.getElementById("empty-title"),
    emptyCopy: document.getElementById("empty-copy"),
    error: document.getElementById("error-state"),
    errorCopy: document.getElementById("error-copy"),
    count: document.getElementById("result-count"),
    interestSummary: document.getElementById("interest-summary"),
    search: document.getElementById("search-input"),
    type: document.getElementById("type-filter"),
    city: document.getElementById("city-filter"),
    reset: document.getElementById("reset-filters"),
    retry: document.getElementById("retry-button"),
    quickFilters: [...document.querySelectorAll("[data-quick]")]
  };

  function apiUrl(path) {
    return `${CONFIG.apiBase.replace(/\/$/, "")}${path}`;
  }

  function getToken() {
    for (const key of CONFIG.tokenStorageKeys) {
      const token = localStorage.getItem(key);
      if (token) return token;
    }
    return "";
  }

  async function fetchJson(path) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), CONFIG.requestTimeoutMs);
    const headers = { "Accept": "application/json" };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    try {
      const response = await fetch(apiUrl(path), {
        method: "GET",
        headers,
        signal: controller.signal,
        credentials: "same-origin"
      });

      if (!response.ok) {
        const error = new Error(`Request to ${path} failed (${response.status}).`);
        error.status = response.status;
        throw error;
      }
      return await response.json();
    } finally {
      clearTimeout(timeout);
    }
  }

  // DRF commonly returns arrays directly or paginated objects with a "results" array.
  function unwrapList(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return [];
    for (const key of ["results", "items", "data", "recommendations"]) {
      if (Array.isArray(payload[key])) return payload[key];
    }
    return [];
  }

  function normaliseText(value) {
    if (value === null || value === undefined) return "";
    if (typeof value === "string" || typeof value === "number") return String(value).trim();
    if (Array.isArray(value)) return value.map(normaliseText).filter(Boolean).join(" ");
    if (typeof value === "object") {
      return normaliseText(value.name ?? value.title ?? value.label ?? value.interest ?? value.slug ?? "");
    }
    return "";
  }

  function getInterestsFromStorage() {
    // Adjust this section if your login/profile code uses a different localStorage shape.
    for (const key of ["travelbuddy_user", "currentUser", "user"]) {
      try {
        const raw = localStorage.getItem(key);
        if (!raw) continue;
        const user = JSON.parse(raw);
        const interests = user.interests ?? user.user_interests ?? user.interest_names ?? [];
        if (Array.isArray(interests)) return interests.map(normaliseText).filter(Boolean);
      } catch (_) {
        // Ignore invalid/non-JSON storage values; API results can still be displayed.
      }
    }
    return [];
  }

  function itemInterests(item) {
    const value = item.interests ?? item.interest ?? item.categories ?? item.tags ?? [];
    return (Array.isArray(value) ? value : [value]).map(normaliseText).filter(Boolean);
  }

  function normaliseItem(item, type) {
    const isEvent = type === "event" || item.type === "event" || item.item_type === "event";
    const id = item.id ?? item.pk ?? item.uuid;
    return {
      ...item,
      _type: isEvent ? "event" : "destination",
      _id: id,
      _title: normaliseText(item.name ?? item.title ?? item.destination_name ?? item.event_name) || (isEvent ? "Untitled event" : "Untitled destination"),
      _description: normaliseText(item.description ?? item.summary ?? item.about),
      _city: normaliseText(item.city ?? item.location_city ?? item.destination?.city),
      _price: item.price ?? item.cost ?? item.ticket_price ?? item.budget,
      _rating: item.rating ?? item.average_rating ?? item.avg_rating,
      _image: normaliseText(item.image_url ?? item.image ?? item.cover_image ?? item.photo),
      _interests: itemInterests(item),
      _start: item.start_date ?? item.start_datetime ?? item.date ?? item.event_date,
      _end: item.end_date ?? item.end_datetime,
      _date: item.date ?? item.start_date ?? item.start_datetime ?? item.event_date
    };
  }

  function interestMatches(item, interests) {
    if (!interests.length) return false;
    const wanted = interests.map(x => x.toLowerCase());
    return item._interests.some(interest => {
      const candidate = interest.toLowerCase();
      return wanted.some(target => candidate === target || candidate.includes(target) || target.includes(candidate));
    });
  }

  function dedupeItems(items) {
    const seen = new Set();
    return items.filter(item => {
      const key = `${item._type}:${item._id ?? item._title}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  async function loadRecommendations() {
    setLoading(true);
    hideAllStates();

    try {
      const interests = getInterestsFromStorage();
      state.userInterests = interests;
      updateInterestSummary();

      // Prefer server-side recommendations if that route exists and returns data.
      try {
        const payload = await fetchJson(CONFIG.recommendationsPath);
        const source = Array.isArray(payload)
          ? payload
          : [
              ...(Array.isArray(payload?.destinations) ? payload.destinations.map(x => ({ ...x, type: "destination" })) : []),
              ...(Array.isArray(payload?.events) ? payload.events.map(x => ({ ...x, type: "event" })) : []),
              ...((!payload?.destinations && !payload?.events) ? unwrapList(payload) : [])
            ];
        const recommended = source.map(item => normaliseItem(item, item.type ?? item.item_type));
        if (recommended.length) {
          state.items = dedupeItems(recommended);
          renderFilteredItems();
          setLoading(false);
          return;
        }
      } catch (error) {
        // Expected while the team is still implementing the endpoint; try listing APIs below.
        console.info("Recommendation endpoint unavailable; trying listing endpoints.", error.message);
      }

      const [destinationsResult, eventsResult] = await Promise.allSettled([
        fetchJson(CONFIG.destinationsPath),
        fetchJson(CONFIG.eventsPath)
      ]);
      const available = [];
      const failures = [];
      if (destinationsResult.status === "fulfilled") {
        available.push(...unwrapList(destinationsResult.value).map(x => normaliseItem(x, "destination")));
      } else failures.push(destinationsResult.reason);
      if (eventsResult.status === "fulfilled") {
        available.push(...unwrapList(eventsResult.value).map(x => normaliseItem(x, "event")));
      } else failures.push(eventsResult.reason);

      if (!available.length) {
        throw failures[0] || new Error("No recommendation or listing endpoint returned data.");
      }

      const unique = dedupeItems(available);
      // When interests are available, rank matches first. Do not hide all listings if nothing matches.
      const matches = interests.length ? unique.filter(item => interestMatches(item, interests)) : [];
      state.items = matches.length
        ? [...matches, ...unique.filter(item => !interestMatches(item, interests))]
        : unique;
      renderFilteredItems();
    } catch (error) {
      console.error("Unable to load TravelBuddy recommendations:", error);
      showError(error);
    } finally {
      setLoading(false);
    }
  }

  function updateInterestSummary() {
    if (!state.userInterests.length) {
      els.interestSummary.textContent = "Add interests to your profile for more relevant suggestions.";
      return;
    }
    const preview = state.userInterests.slice(0, 4).join(", ");
    const remainder = state.userInterests.length > 4 ? ` +${state.userInterests.length - 4} more` : "";
    els.interestSummary.textContent = `Using your interests: ${preview}${remainder}.`;
  }

  function setLoading(isLoading) {
    state.loading = isLoading;
    if (isLoading) {
      els.status.hidden = false;
      els.grid.hidden = true;
      els.empty.hidden = true;
      els.error.hidden = true;
      els.count.textContent = "Loading picks…";
    }
  }

  function hideAllStates() {
    els.status.hidden = true;
    els.grid.hidden = true;
    els.empty.hidden = true;
    els.error.hidden = true;
  }

  function showError(error) {
    hideAllStates();
    els.error.hidden = false;
    els.count.textContent = "Unavailable";
    const message = error?.name === "AbortError"
      ? "The request took too long. Check that the backend is running, then try again."
      : error?.status === 401 || error?.status === 403
        ? "The API requires authentication. Sign in and check that the frontend is sending the token your backend expects."
        : "The recommendations and listing endpoints could not be reached. Check the API paths and that Django is running.";
    els.errorCopy.textContent = message;
  }

  function safeDate(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return normaliseText(value);
    return new Intl.DateTimeFormat("en-ZA", { day: "numeric", month: "short", year: "numeric" }).format(date);
  }

  function safePrice(value) {
    if (value === null || value === undefined || value === "") return "Price varies";
    const number = Number(value);
    if (!Number.isFinite(number)) return normaliseText(value);
    return number === 0 ? "Free" : `R${number.toLocaleString("en-ZA", { maximumFractionDigits: 2 })}`;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
  }

  function detailUrl(item) {
    const path = item._type === "event" ? CONFIG.eventDetailPath : CONFIG.destinationDetailPath;
    const id = item._id;
    return id === undefined || id === null
      ? path
      : `${path}?id=${encodeURIComponent(id)}`;
  }

  function cardMarkup(item) {
    const isEvent = item._type === "event";
    const icon = isEvent ? "fa-calendar-days" : "fa-mountain-sun";
    const typeLabel = isEvent ? "EVENT" : "DESTINATION";
    const location = item._city ? `<span><i class="fa-solid fa-location-dot"></i>${escapeHtml(item._city)}</span>` : "";
    const date = isEvent ? safeDate(item._date || item._start) : "";
    const dateMeta = date ? `<span><i class="fa-regular fa-calendar"></i>${escapeHtml(date)}</span>` : "";
    const ratingNumber = Number(item._rating);
    const rating = item._rating !== null && item._rating !== undefined && item._rating !== "" && Number.isFinite(ratingNumber)
      ? `<span class="card-rating"><i class="fa-solid fa-star"></i>${ratingNumber.toFixed(1)}</span>` : "";
    const image = item._image
      ? `<img class="card-image" src="${escapeHtml(item._image)}" alt="${escapeHtml(item._title)}" loading="lazy" onerror="this.remove(); this.parentElement.insertAdjacentHTML('afterbegin','<div class=&quot;image-placeholder&quot;><i class=&quot;fa-solid ${icon}&quot;></i></div>')">`
      : `<div class="image-placeholder"><i class="fa-solid ${icon}"></i></div>`;
    const description = item._description || (isEvent ? "Discover the details and see whether this event belongs on your calendar." : "Explore the details and see whether this destination belongs on your next trip.");
    const interestBadges = item._interests.slice(0, 2).map(x => `<span class="interest-tag">${escapeHtml(x)}</span>`).join("");

    return `
      <article class="recommendation-card">
        <div class="card-image-wrap">
          ${image}
          <span class="card-type"><i class="fa-solid ${icon}"></i>${typeLabel}</span>
        </div>
        <div class="card-body">
          <div class="card-meta">${location}${dateMeta}${rating}</div>
          <h3 class="card-title">${escapeHtml(item._title)}</h3>
          <p class="card-description">${escapeHtml(description)}</p>
          ${interestBadges ? `<div class="card-meta">${interestBadges}</div>` : ""}
          <div class="card-bottom">
            <span class="card-price">${escapeHtml(safePrice(item._price))}${item._price !== null && item._price !== undefined && Number(item._price) > 0 ? ' <small>per person / listed price</small>' : ""}</span>
            <span class="card-rating">${isEvent ? "Make a plan" : "Worth exploring"}</span>
          </div>
          <a class="card-link" href="${escapeHtml(detailUrl(item))}">View ${isEvent ? "event" : "destination"} <i class="fa-solid fa-arrow-right"></i></a>
        </div>
      </article>`;
  }

  function renderFilteredItems() {
    const query = els.search.value.trim().toLowerCase();
    const type = els.type.value;
    const city = els.city.value.trim().toLowerCase();

    state.filteredItems = state.items.filter(item => {
      if (type !== "all" && item._type !== type) return false;
      if (state.activeQuickFilter !== "all" && item._type !== state.activeQuickFilter) return false;
      if (city && !item._city.toLowerCase().includes(city)) return false;
      if (query) {
        const searchable = [
          item._title, item._description, item._city, ...item._interests
        ].join(" ").toLowerCase();
        if (!searchable.includes(query)) return false;
      }
      return true;
    });

    hideAllStates();
    els.count.textContent = `${state.filteredItems.length} ${state.filteredItems.length === 1 ? "pick" : "picks"}`;

    if (!state.filteredItems.length) {
      els.empty.hidden = false;
      els.emptyTitle.textContent = state.items.length ? "No matches for those filters" : "No recommendations yet";
      els.emptyCopy.textContent = state.items.length
        ? "Try a different search, clear the city filter, or switch back to all recommendations."
        : "Add interests to your profile or check back once destinations and events have been added.";
      return;
    }

    els.grid.innerHTML = state.filteredItems.map(cardMarkup).join("");
    els.grid.hidden = false;
  }

  function resetFilters() {
    els.search.value = "";
    els.type.value = "all";
    els.city.value = "";
    state.activeQuickFilter = "all";
    els.quickFilters.forEach(button => button.classList.toggle("active", button.dataset.quick === "all"));
    renderFilteredItems();
  }

  els.search.addEventListener("input", renderFilteredItems);
  els.type.addEventListener("change", () => {
    state.activeQuickFilter = "all";
    els.quickFilters.forEach(button => button.classList.toggle("active", button.dataset.quick === "all"));
    renderFilteredItems();
  });
  els.city.addEventListener("input", renderFilteredItems);
  els.reset.addEventListener("click", resetFilters);
  els.retry.addEventListener("click", loadRecommendations);
  els.quickFilters.forEach(button => {
    button.addEventListener("click", () => {
      state.activeQuickFilter = button.dataset.quick;
      els.quickFilters.forEach(item => item.classList.toggle("active", item === button));
      els.type.value = "all";
      renderFilteredItems();
    });
  });

  loadRecommendations();
})();
