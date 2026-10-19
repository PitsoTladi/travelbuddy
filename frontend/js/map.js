
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000/api/map/locations/";

    const mapElement = document.getElementById("map");
    const statusElement = document.getElementById("map-status");
    const countElement = document.getElementById("location-count");
    const resetButton = document.getElementById("reset-map");
    const filterButtons = document.querySelectorAll("[data-filter]");

    if (!mapElement || !statusElement || !countElement || !resetButton) {
        console.error("Map page is missing one or more required HTML elements.");
        return;
    }

    if (typeof L === "undefined") {
        showStatus(
            "The map library could not load. Check your internet connection and refresh.",
            "error"
        );
        return;
    }

    const DEFAULT_CENTER = [-26.2041, 28.0473];
    const DEFAULT_ZOOM = 6;

    const map = L.map("map", {
        scrollWheelZoom: true
    }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markerLayers = {
        destination: L.layerGroup().addTo(map),
        event: L.layerGroup().addTo(map)
    };

    let allLocations = [];
    let activeFilter = "all";
    let visibleLocations = [];

    function showStatus(message, type = "") {
        statusElement.textContent = message;
        statusElement.className = "map-status";

        if (type) {
            statusElement.classList.add(type);
        }
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;"
            };

            return entities[character];
        });
    }

    function formatPrice(price) {
        const amount = Number(price);

        if (!Number.isFinite(amount)) {
            return "Price unavailable";
        }

        if (amount === 0) {
            return "Free";
        }

        return new Intl.NumberFormat("en-ZA", {
            style: "currency",
            currency: "ZAR"
        }).format(amount);
    }

    function isValidLocation(location) {
        if (!location || typeof location !== "object") {
            return false;
        }

        const latitude = Number(location.latitude);
        const longitude = Number(location.longitude);

        return (
            (location.type === "destination" || location.type === "event") &&
            typeof location.name === "string" &&
            location.name.trim().length > 0 &&
            Number.isFinite(latitude) &&
            Number.isFinite(longitude) &&
            latitude >= -90 &&
            latitude <= 90 &&
            longitude >= -180 &&
            longitude <= 180
        );
    }

    function createPopup(location) {
        const typeLabel =
            location.type === "event" ? "Event" : "Destination";

        const typeClass = location.type === "event" ? "event" : "";

        const description = location.description
            ? `<p class="popup-description">${escapeHTML(location.description)}</p>`
            : "";

        const city = location.city
            ? `<p class="popup-meta">${escapeHTML(location.city)}</p>`
            : "";

        return `
            <div class="map-popup">
                <p class="popup-type ${typeClass}">${typeLabel}</p>
                <h3 class="popup-title">${escapeHTML(location.name)}</h3>
                ${description}
                ${city}
                <p class="popup-meta">${escapeHTML(formatPrice(location.price))}</p>
            </div>
        `;
    }

    function createMarker(location) {
        const coordinates = [
            Number(location.latitude),
            Number(location.longitude)
        ];

        const color = location.type === "event" ? "#d97736" : "#2b8258";

        const markerIcon = L.divIcon({
            className: "custom-map-marker",
            html: `
                <span style="
                    display: block;
                    width: 18px;
                    height: 18px;
                    background: ${color};
                    border: 3px solid white;
                    border-radius: 50%;
                    box-shadow: 0 2px 7px rgba(0,0,0,0.35);
                "></span>
            `,
            iconSize: [18, 18],
            iconAnchor: [9, 9],
            popupAnchor: [0, -10]
        });

        return L.marker(coordinates, {
            icon: markerIcon,
            title: location.name,
            alt: `${location.name}, ${location.type}`
        }).bindPopup(createPopup(location));
    }

    function updateCount() {
        countElement.textContent = String(visibleLocations.length);
    }

    function renderMarkers() {
        markerLayers.destination.clearLayers();
        markerLayers.event.clearLayers();

        visibleLocations = allLocations.filter((location) => {
            return activeFilter === "all" || location.type === activeFilter;
        });

        visibleLocations.forEach((location) => {
            const marker = createMarker(location);
            markerLayers[location.type].addLayer(marker);
        });

        updateCount();

        if (visibleLocations.length === 0) {
            showStatus(
                allLocations.length === 0
                    ? "No mapped locations are available yet. Add coordinates to destinations or events to display them here."
                    : `No ${activeFilter}s found. Try another filter.`,
                "success"
            );
            return;
        }

        showStatus(
            `Showing ${visibleLocations.length} ${
                visibleLocations.length === 1 ? "location" : "locations"
            }.`,
            "success"
        );

        const markers = visibleLocations.map((location) => [
            Number(location.latitude),
            Number(location.longitude)
        ]);

        if (markers.length === 1) {
    map.setView(markers[0], 12);
} else {
    const bounds = L.latLngBounds(markers);

    map.fitBounds(bounds, {
        padding: [35, 35],
        maxZoom: 12
    });

    // Prevent widely scattered dummy coordinates from
    // zooming the map out beyond a useful viewing level.
    if (map.getZoom() < 6) {
        map.setView([-26.2041, 28.0473], 6);
    }
}
    }

    function updateActiveFilter(selectedButton) {
        filterButtons.forEach((button) => {
            const isActive = button === selectedButton;

            button.classList.toggle("active", isActive);
            button.setAttribute("aria-pressed", String(isActive));
        });
    }

    async function loadLocations() {
        showStatus("Loading destinations and events…");

        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            });

            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                throw new Error("The map API returned an unexpected response.");
            }

            allLocations = data.filter(isValidLocation);

            if (allLocations.length !== data.length) {
                console.warn(
                    `${data.length - allLocations.length} invalid map records were ignored.`
                );
            }

            renderMarkers();
        } catch (error) {
            console.error("Unable to load map locations:", error);
            allLocations = [];
            visibleLocations = [];
            markerLayers.destination.clearLayers();
            markerLayers.event.clearLayers();
            updateCount();

            showStatus(
                "We couldn't load locations. Check that the Django server is running and the map API is reachable, then refresh.",
                "error"
            );
        }
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter;
            updateActiveFilter(button);
            renderMarkers();
        });
    });

    resetButton.addEventListener("click", () => {
        if (visibleLocations.length === 0) {
            map.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
            return;
        }

        const coordinates = visibleLocations.map((location) => [
            Number(location.latitude),
            Number(location.longitude)
        ]);

        if (coordinates.length === 1) {
            map.setView(coordinates[0], 12);
        } else {
            map.fitBounds(L.latLngBounds(coordinates), {
                padding: [35, 35],
                maxZoom: 12
            });
        }
    });

    loadLocations();
});
